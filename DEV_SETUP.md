# Development Environment Setup

This directory contains a utility script to set up your local development environment with all required tools.

## Quick Start

Run the setup script:

```bash
./setup-dev-env.sh
```

## What Gets Installed

The script will install:

1. **NVM (Node Version Manager)**
   - Latest version from https://github.com/nvm-sh/nvm
   - Allows you to manage multiple Node.js versions
   - Auto-configures your shell

2. **Node.js LTS**
   - Latest Long Term Support version
   - Includes npm (Node Package Manager)
   - Set as default version

3. **Bun**
   - Ultra-fast JavaScript runtime and package manager
   - Used for building the frontend
   - Faster than npm/yarn

4. **Frontend Dependencies**
   - Automatically installs all React/TypeScript packages
   - Installs from `frontend/package.json`

## Prerequisites

- Linux system (Ubuntu/Debian recommended)
- `sudo` access for installing system packages
- Internet connection

## Manual Installation (Alternative)

If you prefer to install manually:

### Install NVM
```bash
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.7/install.sh | bash
source ~/.bashrc
```

### Install Node.js LTS
```bash
nvm install --lts
nvm use --lts
nvm alias default 'lts/*'
```

### Install Bun
```bash
curl -fsSL https://bun.sh/install | bash
source ~/.bashrc
```

### Install Frontend Dependencies
```bash
cd frontend
bun install
# or
npm install
```

## Verification

After installation, verify everything works:

```bash
# Check Node.js
node --version

# Check npm
npm --version

# Check Bun
bun --version

# Check NVM
nvm --version
```

## Usage

### Using NVM

```bash
# List installed versions
nvm ls

# List available versions
nvm ls-remote

# Install specific version
nvm install 18.17.0

# Switch to version
nvm use 18.17.0

# Set default version
nvm alias default 18.17.0

# Use project's .nvmrc
nvm use
```

### Using Bun

```bash
# Install dependencies
cd frontend
bun install

# Run dev server
bun run dev

# Build for production
bun run build

# Run tests
bun test

# Update Bun itself
bun upgrade
```

### Frontend Development

```bash
# Install dependencies
cd frontend
bun install

# Start development server
bun run dev

# Build for production
bun run build

# Preview production build
bun run preview

# Lint code
bun run lint
```

## Troubleshooting

### NVM command not found
```bash
# Reload shell configuration
source ~/.bashrc
# or
source ~/.zshrc
```

### Bun command not found
```bash
# Add to PATH manually
export BUN_INSTALL="$HOME/.bun"
export PATH="$BUN_INSTALL/bin:$PATH"

# Make permanent
echo 'export BUN_INSTALL="$HOME/.bun"' >> ~/.bashrc
echo 'export PATH="$BUN_INSTALL/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
```

### Permission errors
```bash
# Fix npm permissions
mkdir ~/.npm-global
npm config set prefix '~/.npm-global'
echo 'export PATH=~/.npm-global/bin:$PATH' >> ~/.bashrc
source ~/.bashrc
```

### Network/DNS issues during install
```bash
# Try with different DNS
sudo echo "nameserver 8.8.8.8" >> /etc/resolv.conf

# Or use npm instead of bun
cd frontend
npm install
```

## Uninstallation

### Remove NVM
```bash
rm -rf ~/.nvm
# Remove NVM lines from ~/.bashrc or ~/.zshrc
```

### Remove Bun
```bash
rm -rf ~/.bun
# Remove Bun lines from ~/.bashrc or ~/.zshrc
```

### Remove Node.js (installed via NVM)
```bash
# Just remove NVM (includes all Node versions)
rm -rf ~/.nvm
```

## Additional Resources

- [NVM Documentation](https://github.com/nvm-sh/nvm)
- [Bun Documentation](https://bun.sh/docs)
- [Node.js Documentation](https://nodejs.org/docs)

## Support

If you encounter issues:

1. Check the troubleshooting section above
2. Review script output for error messages
3. Ensure you have internet connection
4. Try manual installation steps
5. Check system requirements (Linux, sudo access)
