# OCR Gaby

A Dockerized Python OCR API service built with FastAPI.

## Features

- 🐳 Fully Dockerized with Docker Compose
- 🚀 FastAPI for high-performance API
- 🔍 OCR capabilities with Tesseract
- 🤖 **Gemini LLM integration** for intelligent text processing
- 💻 **Command-line interface** for direct OCR operations
- 🗄️ PostgreSQL database integration
- 📝 Redis for caching
- 🧪 Testing with pytest
- 🔧 Development tools (Black, Flake8, MyPy)

## Quick Start

### Prerequisites

- Docker and Docker Compose
- Git

### Installation

1. Clone the repository:
```bash
git clone <your-repo-url>
cd ocr-gaby
```

2. Copy environment file:
```bash
cp .env.example .env
```

3. Build and run with Docker Compose:
```bash
docker-compose up --build
```

4. Set up your Gemini API key (optional):
```bash
# Edit .env file and add your Gemini API key
GEMINI_API_KEY=your-api-key-here
```

The API will be available at `http://localhost:8000`

## CLI Usage

### Install CLI Tools

```bash
# Run the setup script
./setup.sh
```

### Basic OCR

```bash
# Extract text from image
ocr-gaby image.jpg

# Extract with preprocessing and Spanish language
ocr-gaby document.png --language spa --preprocess

# Save output to file
ocr-gaby scan.pdf --output extracted.txt

# Get JSON output with detailed information
ocr-gaby image.jpg --format json --verbose
```

### Gemini LLM Integration

```bash
# Analyze extracted text with Gemini
ocr-gaby invoice.jpg --gemini --gemini-task analyze

# Summarize document content
ocr-gaby document.png --gemini --gemini-task summarize

# Extract specific information with custom prompt
ocr-gaby receipt.jpg --gemini --gemini-prompt "Extract all prices, dates, and merchant names"

# Structure and clean up OCR text
ocr-gaby messy-scan.png --gemini --gemini-task structure

# Translate non-English text
ocr-gaby foreign-doc.jpg --gemini --gemini-task translate
```

### Batch Processing

```bash
# Process all images in directory
ocr-gaby-batch /path/to/images/

# Process recursively with Gemini analysis
ocr-gaby-batch /path/to/images/ --recursive --gemini --gemini-task extract

# Parallel processing with custom workers
ocr-gaby-batch /path/to/images/ --workers 4 --output results.json
```

### Available Commands

```bash
# List supported languages
ocr-gaby --languages

# List available Gemini tasks
ocr-gaby --gemini-tasks
```

### API Documentation

Once running, visit:
- API Documentation: `http://localhost:8000/docs`
- Alternative docs: `http://localhost:8000/redoc`

## Development

### Local Development

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate  # Windows
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the application:
```bash
python main.py
```

### Running Tests

```bash
# With Docker
docker-compose exec app pytest

# Locally
pytest
```

### Code Formatting

```bash
# Format code
black .

# Check linting
flake8 .

# Type checking
mypy .
```

## Project Structure

```
ocr-gaby/
├── app/
│   ├── __init__.py
│   ├── config.py      # Application configuration
│   ├── models.py      # Pydantic models
│   └── gemini.py      # Gemini LLM integration
├── tests/
│   └── test_main.py   # Test files
├── cli.py            # Command-line OCR tool
├── batch_cli.py      # Batch processing CLI
├── setup.sh          # CLI installation script
├── .env.example       # Environment variables template
├── docker-compose.yml # Docker Compose configuration
├── Dockerfile         # Docker configuration
├── main.py           # FastAPI application
├── requirements.txt  # Python dependencies
└── README.md         # This file
```

## API Endpoints

- `GET /` - Welcome message
- `GET /health` - Health check
- `POST /ocr` - Extract text from images (coming soon)

## CLI Tools

- `ocr-gaby` - Single image OCR processing with optional Gemini integration
- `ocr-gaby-batch` - Batch processing multiple images

## Gemini LLM Tasks

- `analyze` - Analyze document structure and content
- `summarize` - Create a concise summary
- `structure` - Clean and organize the text
- `extract` - Extract key information and data
- `translate` - Detect language and translate to English
- `validate` - Validate and fact-check information
- `format` - Format into professional document

## Environment Variables

See `.env.example` for all available configuration options.

## Docker Services

- **app**: Main FastAPI application
- **db**: PostgreSQL database
- **redis**: Redis cache

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests
5. Submit a pull request

## License

This project is licensed under the MIT License.