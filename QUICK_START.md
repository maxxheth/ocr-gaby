# OCR Gaby - Quick Start Guide

## ✅ Setup Complete!

Your Dockerized OCR project with Gemini LLM integration is ready to use.

## 🐳 Using with Docker

### Basic OCR Commands

```bash
# Extract text from an image
docker compose exec app python cli.py /path/to/image.jpg

# With preprocessing for better accuracy
docker compose exec app python cli.py image.png --preprocess

# Spanish language OCR
docker compose exec app python cli.py documento.jpg --language spa

# Save output to file
docker compose exec app python cli.py scan.pdf --output result.txt

# JSON format with detailed info
docker compose exec app python cli.py image.jpg --format json --verbose
```

### Gemini LLM Integration

**Important:** Set your Gemini API key first:
```bash
# Option 1: In .env file
echo "GEMINI_API_KEY=your-api-key-here" >> .env

# Option 2: Pass as argument
docker compose exec app python cli.py image.jpg --gemini --gemini-api-key YOUR_KEY
```

**Available Gemini Tasks:**
```bash
# Analyze document (default)
docker compose exec app python cli.py invoice.jpg --gemini

# Summarize content
docker compose exec app python cli.py document.png --gemini --gemini-task summarize

# Extract specific data
docker compose exec app python cli.py receipt.jpg --gemini --gemini-task extract

# Structure and clean text
docker compose exec app python cli.py messy-scan.png --gemini --gemini-task structure

# Translate to English
docker compose exec app python cli.py foreign-doc.jpg --gemini --gemini-task translate

# Custom prompt
docker compose exec app python cli.py bill.jpg --gemini --gemini-prompt "Extract all dates, amounts, and account numbers"
```

### Batch Processing

```bash
# Process all images in a directory
docker compose exec app python batch_cli.py /path/to/images/

# Recursive processing with Gemini
docker compose exec app python batch_cli.py /path/to/images/ --recursive --gemini --gemini-task extract

# Parallel processing (4 workers)
docker compose exec app python batch_cli.py /path/to/images/ --workers 4 --output results.json

# With preprocessing
docker compose exec app python batch_cli.py /path/to/images/ --preprocess --verbose
```

### Utility Commands

```bash
# List available languages
docker compose exec app python cli.py --languages

# List Gemini tasks
docker compose exec app python cli.py --gemini-tasks

# Help
docker compose exec app python cli.py --help
docker compose exec app python batch_cli.py --help
```

## 💻 Using Locally (without Docker)

### Setup

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# or: venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Install Tesseract (if not already installed)
# Ubuntu/Debian:
sudo apt-get install tesseract-ocr tesseract-ocr-eng

# macOS:
brew install tesseract

# Set Gemini API key
export GEMINI_API_KEY=your-api-key-here
```

### Usage

```bash
# Same commands, but without docker compose exec app
python cli.py image.jpg
python cli.py image.jpg --gemini --gemini-task summarize
python batch_cli.py /path/to/images/ --recursive
```

### Install CLI globally (optional)

```bash
# Run the setup script
./setup.sh

# Now you can use:
ocr-gaby image.jpg
ocr-gaby-batch /path/to/images/
```

## 📊 Output Formats

### Text Format (default)
```bash
docker compose exec app python cli.py image.jpg
# Outputs: extracted text only

docker compose exec app python cli.py image.jpg --verbose
# Outputs: text + OCR stats (confidence, word count, etc.)

docker compose exec app python cli.py image.jpg --gemini
# Outputs: OCR text + Gemini analysis
```

### JSON Format
```bash
docker compose exec app python cli.py image.jpg --format json
# Outputs: Complete JSON with all metadata

docker compose exec app python cli.py image.jpg --format json --gemini
# Outputs: JSON including Gemini results
```

## 🚀 API Server (Optional)

Start the FastAPI server:
```bash
docker compose exec app python main.py
```

Access at: http://localhost:8000/docs

## 🛠️ Docker Commands

```bash
# Start services
docker compose up -d

# Stop services
docker compose down

# View logs
docker compose logs -f app

# Rebuild after changes
docker compose up --build -d

# Access container shell
docker compose exec app bash
```

## 📝 Example Workflow

```bash
# 1. Start containers
docker compose up -d

# 2. Set API key (if using Gemini)
echo "GEMINI_API_KEY=your-key" >> .env

# 3. Process a single image
docker compose exec app python cli.py invoice.jpg --gemini --gemini-task extract --verbose

# 4. Batch process a folder
docker compose exec app python batch_cli.py ./documents/ --recursive --gemini --output results.json

# 5. View results
cat results.json
```

## 🔧 Troubleshooting

**Issue: "GEMINI_API_KEY not found"**
```bash
# Make sure .env file has the key
echo "GEMINI_API_KEY=your-api-key" >> .env

# Or pass it directly
docker compose exec app python cli.py image.jpg --gemini --gemini-api-key YOUR_KEY
```

**Issue: "Tesseract not found"**
```bash
# Already installed in Docker container
# For local use, install tesseract-ocr package
```

**Issue: Low OCR confidence**
```bash
# Try preprocessing
docker compose exec app python cli.py image.jpg --preprocess

# Try different PSM mode
docker compose exec app python cli.py image.jpg --config '--psm 3'
```

## 📚 Resources

- Get Gemini API Key: https://ai.google.dev/
- Tesseract Documentation: https://github.com/tesseract-ocr/tesseract
- API Docs: http://localhost:8000/docs (when server is running)

## ⚡ Pro Tips

1. Use `--preprocess` for noisy or low-quality images
2. Use `--format json` for programmatic processing
3. Adjust `--gemini-temperature` (0.0-1.0) for more/less creative responses
4. Use batch processing for multiple files to save time
5. Store API key in `.env` file for convenience
6. Use `--verbose` to debug issues

Enjoy your OCR + AI-powered document processing! 🎉
