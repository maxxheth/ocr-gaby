#!/bin/bash

# OCR Gaby - Development Environment Setup Script
# Installs nvm, Node.js, and Bun for local development

set -e  # Exit on error

echo "=================================================="
echo "  OCR Gaby - Development Environment Setup"
echo "=================================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Function to print colored output
print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_info() {
    echo -e "${BLUE}ℹ${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

# Check if running on Linux
if [[ "$OSTYPE" != "linux-gnu"* ]]; then
    print_warning "This script is designed for Linux. For macOS/Windows, please install manually."
    echo "Visit: https://github.com/nvm-sh/nvm and https://bun.sh"
    exit 1
fi

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

echo "Step 1: Installing prerequisites..."
echo "-----------------------------------"

# Update package lists
print_info "Updating package lists..."
sudo apt-get update -qq

# Install required packages
REQUIRED_PACKAGES="curl wget git build-essential"
print_info "Installing required packages: $REQUIRED_PACKAGES"
sudo apt-get install -y $REQUIRED_PACKAGES

print_success "Prerequisites installed"
echo ""

# Install NVM
echo "Step 2: Installing NVM (Node Version Manager)..."
echo "-------------------------------------------------"

if command_exists nvm || [ -d "$HOME/.nvm" ]; then
    print_warning "NVM already installed. Skipping..."
else
    print_info "Downloading and installing NVM..."
    
    # Get latest NVM version
    NVM_VERSION=$(curl -s https://api.github.com/repos/nvm-sh/nvm/releases/latest | grep '"tag_name"' | sed -E 's/.*"([^"]+)".*/\1/')
    
    if [ -z "$NVM_VERSION" ]; then
        NVM_VERSION="v0.39.7"  # Fallback version
        print_warning "Could not fetch latest version, using $NVM_VERSION"
    fi
    
    curl -o- "https://raw.githubusercontent.com/nvm-sh/nvm/$NVM_VERSION/install.sh" | bash
    
    # Load NVM
    export NVM_DIR="$HOME/.nvm"
    [ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"
    [ -s "$NVM_DIR/bash_completion" ] && \. "$NVM_DIR/bash_completion"
    
    print_success "NVM installed successfully"
fi

# Add NVM to current session if not loaded
if ! command_exists nvm; then
    export NVM_DIR="$HOME/.nvm"
    [ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"
fi

echo ""

# Install Node.js
echo "Step 3: Installing Node.js..."
echo "------------------------------"

if command_exists node; then
    CURRENT_NODE_VERSION=$(node --version)
    print_warning "Node.js already installed: $CURRENT_NODE_VERSION"
    read -p "Do you want to install/update to LTS version? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        print_info "Skipping Node.js installation"
    else
        print_info "Installing Node.js LTS..."
        nvm install --lts
        nvm use --lts
        nvm alias default 'lts/*'
        print_success "Node.js LTS installed"
    fi
else
    print_info "Installing Node.js LTS..."
    nvm install --lts
    nvm use --lts
    nvm alias default 'lts/*'
    print_success "Node.js LTS installed"
fi

NODE_VERSION=$(node --version 2>/dev/null || echo "Not available")
NPM_VERSION=$(npm --version 2>/dev/null || echo "Not available")

print_info "Node.js version: $NODE_VERSION"
print_info "npm version: $NPM_VERSION"

echo ""

# Install Bun
echo "Step 4: Installing Bun..."
echo "-------------------------"

if command_exists bun; then
    CURRENT_BUN_VERSION=$(bun --version)
    print_warning "Bun already installed: v$CURRENT_BUN_VERSION"
    read -p "Do you want to reinstall/update Bun? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        print_info "Skipping Bun installation"
    else
        print_info "Installing/updating Bun..."
        curl -fsSL https://bun.sh/install | bash
        print_success "Bun updated"
    fi
else
    print_info "Installing Bun..."
    curl -fsSL https://bun.sh/install | bash
    print_success "Bun installed"
fi

# Add Bun to PATH for current session
export BUN_INSTALL="$HOME/.bun"
export PATH="$BUN_INSTALL/bin:$PATH"

BUN_VERSION=$(bun --version 2>/dev/null || echo "Not available")
print_info "Bun version: $BUN_VERSION"

echo ""

# Setup shell configuration
echo "Step 5: Configuring shell environment..."
echo "-----------------------------------------"

SHELL_CONFIG=""
if [ -n "$BASH_VERSION" ]; then
    SHELL_CONFIG="$HOME/.bashrc"
elif [ -n "$ZSH_VERSION" ]; then
    SHELL_CONFIG="$HOME/.zshrc"
else
    SHELL_CONFIG="$HOME/.profile"
fi

print_info "Detected shell config: $SHELL_CONFIG"

# Check if NVM is already in shell config
if ! grep -q "NVM_DIR" "$SHELL_CONFIG" 2>/dev/null; then
    print_info "Adding NVM to $SHELL_CONFIG..."
    cat >> "$SHELL_CONFIG" << 'EOF'

# NVM Configuration
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"  # This loads nvm
[ -s "$NVM_DIR/bash_completion" ] && \. "$NVM_DIR/bash_completion"  # This loads nvm bash_completion
EOF
    print_success "NVM added to shell configuration"
else
    print_info "NVM already configured in shell"
fi

# Check if Bun is already in shell config
if ! grep -q "BUN_INSTALL" "$SHELL_CONFIG" 2>/dev/null; then
    print_info "Adding Bun to $SHELL_CONFIG..."
    cat >> "$SHELL_CONFIG" << 'EOF'

# Bun Configuration
export BUN_INSTALL="$HOME/.bun"
export PATH="$BUN_INSTALL/bin:$PATH"
EOF
    print_success "Bun added to shell configuration"
else
    print_info "Bun already configured in shell"
fi

echo ""

# Install frontend dependencies
echo "Step 6: Installing frontend dependencies..."
echo "--------------------------------------------"

if [ -f "frontend/package.json" ]; then
    cd frontend
    print_info "Installing dependencies with Bun..."
    
    if command_exists bun && [ "$BUN_VERSION" != "Not available" ]; then
        bun install
        print_success "Dependencies installed with Bun"
    else
        print_warning "Bun not available, falling back to npm..."
        npm install
        print_success "Dependencies installed with npm"
    fi
    
    cd ..
else
    print_warning "frontend/package.json not found. Skipping dependency installation."
fi

echo ""

# Summary
echo "=================================================="
echo "  Installation Complete!"
echo "=================================================="
echo ""
print_success "Development environment setup successful!"
echo ""
echo "Installed versions:"
echo "  • Node.js: $NODE_VERSION"
echo "  • npm: $NPM_VERSION"
echo "  • Bun: v$BUN_VERSION"
echo ""
echo "Next steps:"
echo "  1. Restart your terminal or run: source $SHELL_CONFIG"
echo "  2. Verify installations:"
echo "     node --version"
echo "     npm --version"
echo "     bun --version"
echo "  3. Start developing!"
echo ""
echo "Useful commands:"
echo "  • Install Node versions:  nvm install <version>"
echo "  • Switch Node versions:   nvm use <version>"
echo "  • List Node versions:     nvm ls"
echo "  • Install dependencies:   cd frontend && bun install"
echo "  • Run dev server:         cd frontend && bun run dev"
echo ""
print_info "For changes to take effect, restart your terminal or run:"
echo "  source $SHELL_CONFIG"
echo ""
