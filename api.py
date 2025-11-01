#!/usr/bin/env python3
"""
OCR Gaby Flask API - REST API for OCR operations
Maps all CLI flags to API endpoints
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.utils import secure_filename
import os
import tempfile
from pathlib import Path
from dotenv import load_dotenv
import json

# Import OCR and Gemini processors
from cli import OCRProcessor
try:
    from app.gemini import GeminiProcessor
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for React frontend

# Configuration
UPLOAD_FOLDER = tempfile.gettempdir()
ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'bmp', 'tiff', 'tif', 'gif', 'webp', 'pdf'}
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB (increased from 10MB)
CHUNK_SIZE = 1024 * 1024  # 1MB chunks for streaming

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE

# Initialize processors
ocr_processor = OCRProcessor()


def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'gemini_available': GEMINI_AVAILABLE,
        'version': '1.0.0'
    })


@app.route('/languages', methods=['GET'])
def get_languages():
    """
    Get available Tesseract languages
    Maps to: --languages flag
    """
    try:
        languages = ocr_processor.get_available_languages()
        return jsonify({
            'success': True,
            'languages': sorted(languages)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/gemini/tasks', methods=['GET'])
def get_gemini_tasks():
    """
    Get available Gemini tasks
    Maps to: --gemini-tasks flag
    """
    if not GEMINI_AVAILABLE:
        return jsonify({
            'success': False,
            'error': 'Gemini integration not available'
        }), 400
    
    tasks = {
        "analyze": "Analyze document structure and content",
        "summarize": "Create a concise summary",
        "structure": "Clean and organize the text",
        "extract": "Extract key information and data",
        "translate": "Detect language and translate to English",
        "validate": "Validate and fact-check information",
        "format": "Format into professional document"
    }
    
    return jsonify({
        'success': True,
        'tasks': tasks
    })


@app.route('/ocr', methods=['POST'])
def process_ocr():
    """
    Process OCR on uploaded image
    
    Maps to CLI flags:
    - file: input_file (required)
    - language: -l, --language
    - config: -c, --config
    - preprocess: -p, --preprocess
    - format: --format
    - verbose: -v, --verbose
    """
    
    # Validate file upload
    if 'file' not in request.files:
        return jsonify({
            'success': False,
            'error': 'No file provided'
        }), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({
            'success': False,
            'error': 'No file selected'
        }), 400
    
    if not allowed_file(file.filename):
        return jsonify({
            'success': False,
            'error': f'File type not allowed. Allowed types: {", ".join(ALLOWED_EXTENSIONS)}'
        }), 400
    
    try:
        # Save uploaded file temporarily
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # Get parameters from request
        language = request.form.get('language', 'eng')
        config = request.form.get('config', '--psm 6')
        preprocess = request.form.get('preprocess', 'false').lower() == 'true'
        verbose = request.form.get('verbose', 'false').lower() == 'true'
        
        # Process OCR
        result = ocr_processor.extract_text(
            filepath,
            language=language,
            config=config,
            preprocess=preprocess
        )
        
        # Clean up temporary file
        os.remove(filepath)
        
        if 'error' in result:
            return jsonify({
                'success': False,
                'error': result['error']
            }), 500
        
        return jsonify({
            'success': True,
            'data': result
        })
        
    except Exception as e:
        # Clean up on error
        if os.path.exists(filepath):
            os.remove(filepath)
        
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/ocr/gemini', methods=['POST'])
def process_ocr_with_gemini():
    """
    Process OCR with Gemini LLM integration
    
    Maps to CLI flags:
    - file: input_file (required)
    - language: -l, --language
    - config: -c, --config
    - preprocess: -p, --preprocess
    - gemini_task: --gemini-task
    - gemini_prompt: --gemini-prompt
    - gemini_temperature: --gemini-temperature
    - gemini_max_tokens: --gemini-max-tokens
    - gemini_api_key: --gemini-api-key
    - verbose: -v, --verbose
    """
    
    if not GEMINI_AVAILABLE:
        return jsonify({
            'success': False,
            'error': 'Gemini integration not available'
        }), 400
    
    # Validate file upload
    if 'file' not in request.files:
        return jsonify({
            'success': False,
            'error': 'No file provided'
        }), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({
            'success': False,
            'error': 'No file selected'
        }), 400
    
    if not allowed_file(file.filename):
        return jsonify({
            'success': False,
            'error': f'File type not allowed. Allowed types: {", ".join(ALLOWED_EXTENSIONS)}'
        }), 400
    
    try:
        # Save uploaded file temporarily
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # Get OCR parameters
        language = request.form.get('language', 'eng')
        config = request.form.get('config', '--psm 6')
        preprocess = request.form.get('preprocess', 'false').lower() == 'true'
        verbose = request.form.get('verbose', 'false').lower() == 'true'
        
        # Get Gemini parameters
        gemini_task = request.form.get('gemini_task', 'analyze')
        gemini_prompt = request.form.get('gemini_prompt', None)
        gemini_temperature = float(request.form.get('gemini_temperature', 0.7))
        gemini_max_tokens = request.form.get('gemini_max_tokens', None)
        if gemini_max_tokens:
            gemini_max_tokens = int(gemini_max_tokens)
        
        gemini_api_key = request.form.get('gemini_api_key') or os.getenv('GEMINI_API_KEY')
        
        if not gemini_api_key:
            os.remove(filepath)
            return jsonify({
                'success': False,
                'error': 'GEMINI_API_KEY not found. Please provide it in the request or set environment variable'
            }), 400
        
        # Process OCR
        ocr_result = ocr_processor.extract_text(
            filepath,
            language=language,
            config=config,
            preprocess=preprocess
        )
        
        # Clean up temporary file
        os.remove(filepath)
        
        if 'error' in ocr_result:
            return jsonify({
                'success': False,
                'error': ocr_result['error']
            }), 500
        
        # Process with Gemini
        gemini = GeminiProcessor(gemini_api_key)
        gemini_result = gemini.process_text(
            ocr_result['text'],
            prompt=gemini_prompt,
            task=gemini_task,
            temperature=gemini_temperature,
            max_tokens=gemini_max_tokens
        )
        
        return jsonify({
            'success': True,
            'data': {
                'ocr': ocr_result,
                'gemini': gemini_result
            }
        })
        
    except Exception as e:
        # Clean up on error
        if os.path.exists(filepath):
            os.remove(filepath)
        
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/batch/ocr', methods=['POST'])
def batch_process():
    """
    Batch process multiple files
    
    Maps to batch_cli.py functionality
    Accepts multiple files in the request
    """
    
    # Validate files
    if 'files' not in request.files:
        return jsonify({
            'success': False,
            'error': 'No files provided'
        }), 400
    
    files = request.files.getlist('files')
    
    if not files or len(files) == 0:
        return jsonify({
            'success': False,
            'error': 'No files selected'
        }), 400
    
    try:
        # Get parameters
        language = request.form.get('language', 'eng')
        config = request.form.get('config', '--psm 6')
        preprocess = request.form.get('preprocess', 'false').lower() == 'true'
        use_gemini = request.form.get('use_gemini', 'false').lower() == 'true'
        gemini_task = request.form.get('gemini_task', 'analyze')
        
        results = []
        failed = []
        
        for file in files:
            if not allowed_file(file.filename):
                failed.append({
                    'filename': file.filename,
                    'error': 'File type not allowed'
                })
                continue
            
            try:
                # Save and process file
                filename = secure_filename(file.filename)
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)
                
                # Process OCR
                result = ocr_processor.extract_text(
                    filepath,
                    language=language,
                    config=config,
                    preprocess=preprocess
                )
                
                result['filename'] = filename
                
                # Process with Gemini if requested
                if use_gemini and GEMINI_AVAILABLE and 'error' not in result:
                    gemini_api_key = os.getenv('GEMINI_API_KEY')
                    if gemini_api_key:
                        gemini = GeminiProcessor(gemini_api_key)
                        gemini_result = gemini.process_text(
                            result['text'],
                            task=gemini_task
                        )
                        result['gemini'] = gemini_result
                
                results.append(result)
                
                # Clean up
                os.remove(filepath)
                
            except Exception as e:
                failed.append({
                    'filename': file.filename,
                    'error': str(e)
                })
                if os.path.exists(filepath):
                    os.remove(filepath)
        
        return jsonify({
            'success': True,
            'data': {
                'total': len(files),
                'processed': len(results),
                'failed': len(failed),
                'results': results,
                'failures': failed
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# === CHUNKED UPLOAD ENDPOINTS ===
# Store for managing chunked uploads
UPLOAD_SESSIONS = {}


@app.route('/upload/init', methods=['POST'])
def init_chunked_upload():
    """
    Initialize a chunked upload session
    Returns an upload_id to use for subsequent chunks
    
    Request body:
    {
        "filename": "image.jpg",
        "filesize": 15728640,
        "chunk_count": 15
    }
    """
    try:
        data = request.json
        filename = secure_filename(data.get('filename', ''))
        filesize = data.get('filesize', 0)
        chunk_count = data.get('chunk_count', 0)
        
        if not filename or not allowed_file(filename):
            return jsonify({
                'success': False,
                'error': 'Invalid filename or file type'
            }), 400
        
        if filesize > MAX_FILE_SIZE:
            return jsonify({
                'success': False,
                'error': f'File too large. Maximum size is {MAX_FILE_SIZE / (1024*1024)}MB'
            }), 400
        
        # Generate unique upload ID
        import uuid
        upload_id = str(uuid.uuid4())
        
        # Create temporary file path
        temp_path = os.path.join(UPLOAD_FOLDER, f'upload_{upload_id}')
        
        # Store session info
        UPLOAD_SESSIONS[upload_id] = {
            'filename': filename,
            'filesize': filesize,
            'chunk_count': chunk_count,
            'received_chunks': [],
            'temp_path': temp_path
        }
        
        return jsonify({
            'success': True,
            'upload_id': upload_id,
            'chunk_size': CHUNK_SIZE
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/upload/chunk/<upload_id>', methods=['POST'])
def upload_chunk(upload_id):
    """
    Upload a single chunk
    
    Form data:
    - chunk: The file chunk
    - chunk_index: Index of this chunk (0-based)
    """
    try:
        if upload_id not in UPLOAD_SESSIONS:
            return jsonify({
                'success': False,
                'error': 'Invalid upload session'
            }), 400
        
        session = UPLOAD_SESSIONS[upload_id]
        
        # Get chunk data
        if 'chunk' not in request.files:
            return jsonify({
                'success': False,
                'error': 'No chunk data provided'
            }), 400
        
        chunk = request.files['chunk']
        chunk_index = int(request.form.get('chunk_index', -1))
        
        if chunk_index < 0:
            return jsonify({
                'success': False,
                'error': 'Invalid chunk index'
            }), 400
        
        # Append chunk to temp file
        temp_path = session['temp_path']
        with open(temp_path, 'ab') as f:
            chunk.save(f)
        
        # Track received chunks
        session['received_chunks'].append(chunk_index)
        
        # Check if all chunks received
        is_complete = len(session['received_chunks']) == session['chunk_count']
        
        return jsonify({
            'success': True,
            'chunk_index': chunk_index,
            'received': len(session['received_chunks']),
            'total': session['chunk_count'],
            'is_complete': is_complete
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/upload/complete/<upload_id>', methods=['POST'])
def complete_chunked_upload(upload_id):
    """
    Complete the chunked upload and process the file
    
    Form data (optional):
    - language: OCR language (default: eng)
    - preprocess: Enable preprocessing (default: false)
    - use_gemini: Enable Gemini analysis (default: false)
    - gemini_task: Gemini task type
    - gemini_prompt: Custom prompt
    """
    try:
        if upload_id not in UPLOAD_SESSIONS:
            return jsonify({
                'success': False,
                'error': 'Invalid upload session'
            }), 400
        
        session = UPLOAD_SESSIONS[upload_id]
        
        # Verify all chunks received
        if len(session['received_chunks']) != session['chunk_count']:
            return jsonify({
                'success': False,
                'error': f"Incomplete upload: {len(session['received_chunks'])}/{session['chunk_count']} chunks received"
            }), 400
        
        # Get processing parameters
        language = request.form.get('language', 'eng')
        preprocess = request.form.get('preprocess', 'false').lower() == 'true'
        use_gemini = request.form.get('use_gemini', 'false').lower() == 'true'
        gemini_task = request.form.get('gemini_task', 'analyze')
        gemini_prompt = request.form.get('gemini_prompt', '')
        
        # Rename temp file to final name
        temp_path = session['temp_path']
        final_path = os.path.join(UPLOAD_FOLDER, session['filename'])
        os.rename(temp_path, final_path)
        
        try:
            # Process the file
            ocr_result = ocr_processor.process_image(
                final_path,
                language=language,
                preprocess=preprocess
            )
            
            response_data = {'ocr': ocr_result}
            
            # Process with Gemini if requested
            if use_gemini and GEMINI_AVAILABLE:
                gemini_processor = GeminiProcessor()
                gemini_result = gemini_processor.process_text(
                    ocr_result['text'],
                    task=gemini_task,
                    custom_prompt=gemini_prompt if gemini_prompt else None
                )
                response_data['gemini'] = gemini_result
            
            # Cleanup
            os.remove(final_path)
            del UPLOAD_SESSIONS[upload_id]
            
            return jsonify({
                'success': True,
                'data': response_data
            })
            
        except Exception as e:
            # Cleanup on error
            if os.path.exists(final_path):
                os.remove(final_path)
            del UPLOAD_SESSIONS[upload_id]
            raise e
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/upload/cancel/<upload_id>', methods=['DELETE'])
def cancel_chunked_upload(upload_id):
    """Cancel a chunked upload and cleanup"""
    try:
        if upload_id not in UPLOAD_SESSIONS:
            return jsonify({
                'success': False,
                'error': 'Invalid upload session'
            }), 400
        
        session = UPLOAD_SESSIONS[upload_id]
        temp_path = session['temp_path']
        
        # Cleanup temp file
        if os.path.exists(temp_path):
            os.remove(temp_path)
        
        # Remove session
        del UPLOAD_SESSIONS[upload_id]
        
        return jsonify({
            'success': True,
            'message': 'Upload cancelled'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


if __name__ == '__main__':
    port = int(os.getenv('API_PORT', 5000))
    debug = os.getenv('DEBUG', 'False').lower() == 'true'
    app.run(host='0.0.0.0', port=port, debug=debug)
