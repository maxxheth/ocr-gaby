#!/bin/bash
# OCR Gaby Setup Script
# Install and configure OCR Gaby CLI tools

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}OCR Gaby CLI Setup${NC}"
echo "================================="

# Check if we're in a Docker container
if [ -f /.dockerenv ]; then
    echo -e "${YELLOW}Running inside Docker container${NC}"
    INSTALL_PREFIX="/usr/local/bin"
else
    echo -e "${YELLOW}Running on host system${NC}"
    INSTALL_PREFIX="$HOME/.local/bin"
    
    # Create local bin directory if it doesn't exist
    mkdir -p "$INSTALL_PREFIX"
    
    # Add to PATH if not already there
    if [[ ":$PATH:" != *":$INSTALL_PREFIX:"* ]]; then
        echo "export PATH=\"$INSTALL_PREFIX:\$PATH\"" >> ~/.bashrc
        echo -e "${YELLOW}Added $INSTALL_PREFIX to PATH in ~/.bashrc${NC}"
        echo -e "${YELLOW}Please run 'source ~/.bashrc' or restart your terminal${NC}"
    fi
fi

# Get the script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

# Install CLI tools
echo -e "\n${GREEN}Installing CLI tools...${NC}"

# Create wrapper scripts
cat > "$INSTALL_PREFIX/ocr-gaby" << EOF
#!/bin/bash
python3 "$SCRIPT_DIR/cli.py" "\$@"
EOF

cat > "$INSTALL_PREFIX/ocr-gaby-batch" << EOF
#!/bin/bash
python3 "$SCRIPT_DIR/batch_cli.py" "\$@"
EOF

# Make executable
chmod +x "$INSTALL_PREFIX/ocr-gaby"
chmod +x "$INSTALL_PREFIX/ocr-gaby-batch"

echo -e "${GREEN}✓ Installed ocr-gaby to $INSTALL_PREFIX/ocr-gaby${NC}"
echo -e "${GREEN}✓ Installed ocr-gaby-batch to $INSTALL_PREFIX/ocr-gaby-batch${NC}"

# Check Tesseract installation
echo -e "\n${GREEN}Checking Tesseract installation...${NC}"

if command -v tesseract &> /dev/null; then
    TESSERACT_VERSION=$(tesseract --version | head -n1)
    echo -e "${GREEN}✓ $TESSERACT_VERSION${NC}"
    
    # List available languages
    echo -e "\n${GREEN}Available languages:${NC}"
    tesseract --list-langs 2>/dev/null | tail -n +2 | head -10
    echo "..."
else
    echo -e "${RED}✗ Tesseract not found${NC}"
    echo -e "${YELLOW}Please install Tesseract OCR:${NC}"
    
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        echo "  sudo apt-get install tesseract-ocr tesseract-ocr-eng"
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        echo "  brew install tesseract"
    else
        echo "  Please visit: https://github.com/tesseract-ocr/tesseract"
    fi
fi

echo -e "\n${GREEN}Setup complete!${NC}"
echo -e "\n${YELLOW}Usage examples:${NC}"
echo "  ocr-gaby image.jpg"
echo "  ocr-gaby image.png --language spa --preprocess"
echo "  ocr-gaby-batch /path/to/images/ --recursive"
echo "  ocr-gaby --languages"