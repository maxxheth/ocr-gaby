#!/usr/bin/env python3
"""
OCR Gaby Batch CLI - Process multiple images in batch
"""

import argparse
import os
import sys
from pathlib import Path
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict, Optional
import time
from cli import OCRProcessor
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import Gemini processor
try:
    from app.gemini import GeminiProcessor
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False


def process_file(file_path: str, ocr: OCRProcessor, args, gemini: Optional['GeminiProcessor'] = None) -> Dict:
    """Process a single file"""
    start_time = time.time()
    
    result = ocr.extract_text(
        file_path,
        language=args.language,
        config=args.config,
        preprocess=args.preprocess
    )
    
    processing_time = time.time() - start_time
    result['file_path'] = file_path
    result['processing_time'] = round(processing_time, 2)
    
    # Process with Gemini if available and requested
    if gemini and not result.get('error') and hasattr(args, 'gemini') and args.gemini:
        try:
            gemini_result = gemini.process_text(
                result['text'],
                prompt=getattr(args, 'gemini_prompt', None),
                task=getattr(args, 'gemini_task', 'analyze'),
                temperature=getattr(args, 'gemini_temperature', 0.7),
                max_tokens=getattr(args, 'gemini_max_tokens', None)
            )
            result['gemini'] = gemini_result
        except Exception as e:
            result['gemini'] = {'success': False, 'error': str(e)}
    
    return result


def find_image_files(directory: str, recursive: bool = False) -> List[str]:
    """Find all image files in directory"""
    image_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif', '.gif', '.webp'}
    
    if recursive:
        pattern = "**/*"
    else:
        pattern = "*"
    
    image_files = []
    for file_path in Path(directory).glob(pattern):
        if file_path.is_file() and file_path.suffix.lower() in image_extensions:
            image_files.append(str(file_path))
    
    return sorted(image_files)


def main():
    parser = argparse.ArgumentParser(
        description='OCR Gaby Batch CLI - Process multiple images',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s /path/to/images/
  %(prog)s /path/to/images/ --recursive --workers 4
  %(prog)s image1.jpg image2.png image3.pdf
  %(prog)s /path/to/images/ --output results.json
  %(prog)s /path/to/images/ --gemini --gemini-task extract
  %(prog)s /path/to/images/ --gemini --gemini-prompt "Find all invoice numbers"
        """
    )
    
    parser.add_argument(
        'inputs',
        nargs='+',
        help='Input files or directories'
    )
    
    parser.add_argument(
        '-l', '--language',
        default='eng',
        help='Tesseract language code (default: eng)'
    )
    
    parser.add_argument(
        '-c', '--config',
        default='--psm 6',
        help='Tesseract configuration (default: --psm 6)'
    )
    
    parser.add_argument(
        '-o', '--output',
        help='Output JSON file path'
    )
    
    parser.add_argument(
        '-p', '--preprocess',
        action='store_true',
        help='Apply image preprocessing'
    )
    
    parser.add_argument(
        '-r', '--recursive',
        action='store_true',
        help='Process directories recursively'
    )
    
    parser.add_argument(
        '-w', '--workers',
        type=int,
        default=2,
        help='Number of worker threads (default: 2)'
    )
    
    parser.add_argument(
        '--tesseract-cmd',
        help='Path to Tesseract executable'
    )
    
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Verbose output'
    )
    
    parser.add_argument(
        '--continue-on-error',
        action='store_true',
        help='Continue processing even if some files fail'
    )
    
    # Gemini integration arguments
    if GEMINI_AVAILABLE:
        parser.add_argument(
            '--gemini',
            action='store_true',
            help='Process OCR results with Gemini LLM'
        )
        
        parser.add_argument(
            '--gemini-task',
            choices=['analyze', 'summarize', 'structure', 'extract', 'translate', 'validate', 'format'],
            default='analyze',
            help='Predefined Gemini task (default: analyze)'
        )
        
        parser.add_argument(
            '--gemini-prompt',
            help='Custom prompt for Gemini processing'
        )
        
        parser.add_argument(
            '--gemini-temperature',
            type=float,
            default=0.7,
            help='Gemini response creativity 0.0-1.0 (default: 0.7)'
        )
        
        parser.add_argument(
            '--gemini-max-tokens',
            type=int,
            help='Maximum tokens in Gemini response'
        )
        
        parser.add_argument(
            '--gemini-api-key',
            help='Gemini API key (or set GEMINI_API_KEY env var)'
        )
    
    args = parser.parse_args()
    
    # Initialize OCR processor
    ocr = OCRProcessor(tesseract_cmd=args.tesseract_cmd)
    
    # Initialize Gemini processor if requested
    gemini = None
    if GEMINI_AVAILABLE and hasattr(args, 'gemini') and args.gemini:
        try:
            api_key = getattr(args, 'gemini_api_key', None) or os.getenv('GEMINI_API_KEY')
            if not api_key:
                print("Error: GEMINI_API_KEY not found. Please set the environment variable or use --gemini-api-key", file=sys.stderr)
                sys.exit(1)
            
            gemini = GeminiProcessor(api_key)
            
            if args.verbose:
                print(f"Gemini integration enabled (task: {getattr(args, 'gemini_task', 'analyze')})")
        
        except Exception as e:
            print(f"Error initializing Gemini: {e}", file=sys.stderr)
            sys.exit(1)
    
    # Collect all files to process
    files_to_process = []
    
    for input_path in args.inputs:
        if os.path.isfile(input_path):
            files_to_process.append(input_path)
        elif os.path.isdir(input_path):
            directory_files = find_image_files(input_path, args.recursive)
            files_to_process.extend(directory_files)
            if args.verbose:
                print(f"Found {len(directory_files)} images in {input_path}")
        else:
            print(f"Warning: {input_path} not found", file=sys.stderr)
    
    if not files_to_process:
        print("No files to process", file=sys.stderr)
        sys.exit(1)
    
    if args.verbose:
        print(f"Processing {len(files_to_process)} files with {args.workers} workers")
        print("-" * 50)
    
    # Process files
    results = []
    failed_files = []
    
    with ThreadPoolExecutor(max_workers=args.workers) as executor:
        # Submit all jobs
        future_to_file = {
            executor.submit(process_file, file_path, ocr, args, gemini): file_path
            for file_path in files_to_process
        }
        
        # Process completed jobs
        for future in as_completed(future_to_file):
            file_path = future_to_file[future]
            
            try:
                result = future.result()
                
                if 'error' in result:
                    failed_files.append((file_path, result['error']))
                    if not args.continue_on_error:
                        print(f"Error processing {file_path}: {result['error']}", file=sys.stderr)
                        sys.exit(1)
                    elif args.verbose:
                        print(f"Failed: {file_path} - {result['error']}")
                else:
                    results.append(result)
                    if args.verbose:
                        confidence = result.get('confidence', 0)
                        words = result.get('word_count', 0)
                        time_taken = result.get('processing_time', 0)
                        
                        # Check if Gemini was used
                        gemini_info = ""
                        if 'gemini' in result:
                            if result['gemini']['success']:
                                gemini_info = " + Gemini"
                            else:
                                gemini_info = " + Gemini (failed)"
                        
                        print(f"✓ {file_path} - {confidence}% confidence, {words} words, {time_taken}s{gemini_info}")
                
            except Exception as e:
                failed_files.append((file_path, str(e)))
                if not args.continue_on_error:
                    print(f"Error processing {file_path}: {e}", file=sys.stderr)
                    sys.exit(1)
                elif args.verbose:
                    print(f"Failed: {file_path} - {e}")
    
    # Summary
    total_files = len(files_to_process)
    successful_files = len(results)
    failed_count = len(failed_files)
    
    summary = {
        'summary': {
            'total_files': total_files,
            'successful': successful_files,
            'failed': failed_count,
            'success_rate': round((successful_files / total_files) * 100, 2) if total_files > 0 else 0
        },
        'results': results
    }
    
    if failed_files:
        summary['failed_files'] = [{'file': f, 'error': e} for f, e in failed_files]
    
    # Output results
    if args.output:
        try:
            with open(args.output, 'w', encoding='utf-8') as f:
                json.dump(summary, f, indent=2, ensure_ascii=False)
            print(f"Results saved to: {args.output}")
        except Exception as e:
            print(f"Error saving results: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        print(json.dumps(summary, indent=2, ensure_ascii=False))
    
    # Print summary
    if args.verbose:
        print("\n" + "=" * 50)
        print(f"Summary: {successful_files}/{total_files} files processed successfully")
        if failed_count > 0:
            print(f"Failed files: {failed_count}")
            for file_path, error in failed_files:
                print(f"  - {file_path}: {error}")


if __name__ == '__main__':
    main()