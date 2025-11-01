#!/usr/bin/env python3
"""
OCR Gaby CLI - Command line interface for OCR operations using Tesseract
"""

import argparse
import sys
import os
from pathlib import Path
import pytesseract
from PIL import Image
import cv2
import numpy as np
from typing import Optional, List
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import Gemini processor
try:
    from app.gemini import GeminiProcessor
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False


class OCRProcessor:
    """Handle OCR operations with Tesseract"""
    
    def __init__(self, tesseract_cmd: Optional[str] = None):
        if tesseract_cmd:
            pytesseract.pytesseract.tesseract_cmd = tesseract_cmd
    
    def extract_text(
        self, 
        image_path: str, 
        language: str = 'eng',
        config: str = '--psm 6',
        preprocess: bool = False
    ) -> dict:
        """Extract text from image using Tesseract"""
        
        try:
            # Load image
            if preprocess:
                image = self._preprocess_image(image_path)
            else:
                image = Image.open(image_path)
            
            # Extract text
            text = pytesseract.image_to_string(
                image, 
                lang=language, 
                config=config
            )
            
            # Get confidence data
            data = pytesseract.image_to_data(
                image, 
                lang=language, 
                config=config,
                output_type=pytesseract.Output.DICT
            )
            
            # Calculate average confidence
            confidences = [int(conf) for conf in data['conf'] if int(conf) > 0]
            avg_confidence = sum(confidences) / len(confidences) if confidences else 0
            
            return {
                'text': text.strip(),
                'confidence': round(avg_confidence, 2),
                'word_count': len(text.split()),
                'character_count': len(text),
                'language': language,
                'config': config
            }
            
        except Exception as e:
            return {
                'error': str(e),
                'text': '',
                'confidence': 0
            }
    
    def _preprocess_image(self, image_path: str) -> Image.Image:
        """Preprocess image to improve OCR accuracy"""
        
        # Read image with OpenCV
        img = cv2.imread(image_path)
        
        # Convert to grayscale
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # Apply noise reduction
        denoised = cv2.medianBlur(gray, 5)
        
        # Apply thresholding
        _, thresh = cv2.threshold(denoised, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        # Convert back to PIL Image
        return Image.fromarray(thresh)
    
    def get_available_languages(self) -> List[str]:
        """Get list of available Tesseract languages"""
        try:
            return pytesseract.get_languages()
        except Exception as e:
            print(f"Error getting languages: {e}")
            return ['eng']  # Default fallback


def main():
    parser = argparse.ArgumentParser(
        description='OCR Gaby CLI - Extract text from images using Tesseract',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s image.jpg
  %(prog)s image.png --language spa --preprocess
  %(prog)s document.pdf --config '--psm 4' --output result.txt
  %(prog)s image.jpg --gemini --gemini-task summarize
  %(prog)s scan.png --gemini --gemini-prompt "Extract all phone numbers and emails"
  %(prog)s --languages
        """
    )
    
    parser.add_argument(
        'input_file',
        nargs='?',
        help='Input image file path'
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
        help='Output file path (optional)'
    )
    
    parser.add_argument(
        '-p', '--preprocess',
        action='store_true',
        help='Apply image preprocessing for better OCR'
    )
    
    parser.add_argument(
        '--format',
        choices=['text', 'json'],
        default='text',
        help='Output format (default: text)'
    )
    
    parser.add_argument(
        '--languages',
        action='store_true',
        help='List available Tesseract languages'
    )
    
    if GEMINI_AVAILABLE:
        parser.add_argument(
            '--gemini-tasks',
            action='store_true',
            help='List available Gemini tasks'
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
    
    # Handle language listing
    if args.languages:
        languages = ocr.get_available_languages()
        print("Available Tesseract languages:")
        for lang in sorted(languages):
            print(f"  {lang}")
        return
    
    # Handle Gemini tasks listing
    if GEMINI_AVAILABLE and hasattr(args, 'gemini_tasks') and args.gemini_tasks:
        try:
            # Test API key
            api_key = getattr(args, 'gemini_api_key', None) or os.getenv('GEMINI_API_KEY')
            if api_key:
                gemini = GeminiProcessor(api_key)
                tasks = gemini.get_available_tasks()
                print("Available Gemini tasks:")
                for task, description in tasks.items():
                    print(f"  {task:<12} - {description}")
            else:
                print("Available Gemini tasks (API key required to test connection):")
                # Show tasks without testing connection
                tasks = {
                    "analyze": "Analyze document structure and content",
                    "summarize": "Create a concise summary",
                    "structure": "Clean and organize the text",
                    "extract": "Extract key information and data",
                    "translate": "Detect language and translate to English",
                    "validate": "Validate and fact-check information",
                    "format": "Format into professional document"
                }
                for task, description in tasks.items():
                    print(f"  {task:<12} - {description}")
        except Exception as e:
            print(f"Error accessing Gemini: {e}", file=sys.stderr)
        return
    
    # Validate input file
    if not args.input_file:
        parser.error("Input file is required (use --languages to list available languages)")
    
    if not os.path.exists(args.input_file):
        print(f"Error: File '{args.input_file}' not found", file=sys.stderr)
        sys.exit(1)
    
    # Check if it's an image file
    image_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif', '.gif', '.webp'}
    file_ext = Path(args.input_file).suffix.lower()
    
    if file_ext not in image_extensions:
        print(f"Warning: '{args.input_file}' may not be a supported image format", file=sys.stderr)
    
    if args.verbose:
        print(f"Processing: {args.input_file}")
        print(f"Language: {args.language}")
        print(f"Config: {args.config}")
        print(f"Preprocess: {args.preprocess}")
        print("-" * 50)
    
    # Extract text
    result = ocr.extract_text(
        args.input_file,
        language=args.language,
        config=args.config,
        preprocess=args.preprocess
    )
    
    # Handle errors
    if 'error' in result:
        print(f"Error: {result['error']}", file=sys.stderr)
        sys.exit(1)
    
    # Process with Gemini if requested
    gemini_result = None
    if GEMINI_AVAILABLE and args.gemini:
        try:
            # Set up Gemini processor
            api_key = args.gemini_api_key or os.getenv('GEMINI_API_KEY')
            if not api_key:
                print("Error: GEMINI_API_KEY not found. Please set the environment variable or use --gemini-api-key", file=sys.stderr)
                sys.exit(1)
            
            gemini = GeminiProcessor(api_key)
            
            if args.verbose:
                print(f"Processing with Gemini (task: {args.gemini_task})...")
            
            gemini_result = gemini.process_text(
                result['text'],
                prompt=args.gemini_prompt,
                task=args.gemini_task,
                temperature=args.gemini_temperature,
                max_tokens=args.gemini_max_tokens
            )
            
            if not gemini_result['success']:
                print(f"Gemini processing failed: {gemini_result['error']}", file=sys.stderr)
                if not args.verbose:
                    sys.exit(1)
            
        except Exception as e:
            print(f"Error initializing Gemini: {e}", file=sys.stderr)
            if not args.verbose:
                sys.exit(1)
    
    # Format output
    if args.format == 'json':
        # Include Gemini results in JSON output
        if gemini_result:
            result['gemini'] = gemini_result
        output = json.dumps(result, indent=2, ensure_ascii=False)
    else:
        # Text format output
        if gemini_result and gemini_result['success']:
            output = f"=== OCR TEXT ===\n{result['text']}\n\n=== GEMINI ANALYSIS ===\n{gemini_result['response']}"
        else:
            output = result['text']
        
        if args.verbose:
            output += f"\n\n--- OCR Info ---"
            output += f"\nConfidence: {result['confidence']}%"
            output += f"\nWords: {result['word_count']}"
            output += f"\nCharacters: {result['character_count']}"
            
            if gemini_result:
                output += f"\n\n--- Gemini Info ---"
                if gemini_result['success']:
                    usage = gemini_result.get('usage', {})
                    output += f"\nTask: {gemini_result['task']}"
                    output += f"\nPrompt tokens: {usage.get('prompt_tokens', 'N/A')}"
                    output += f"\nCompletion tokens: {usage.get('completion_tokens', 'N/A')}"
                else:
                    output += f"\nError: {gemini_result['error']}"
    
    # Save or print output
    if args.output:
        try:
            with open(args.output, 'w', encoding='utf-8') as f:
                f.write(output)
            print(f"Output saved to: {args.output}")
        except Exception as e:
            print(f"Error saving output: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        print(output)


if __name__ == '__main__':
    main()