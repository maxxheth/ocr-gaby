#!/bin/bash
# Complete Frontend Setup Script

echo "🚀 Completing OCR Gaby Frontend Setup..."

cd /var/www/ocr-gaby/frontend

# Check if bun is available
if ! command -v bun &> /dev/null; then
    export PATH="$HOME/.bun/bin:$PATH"
fi

echo "📦 Installing dependencies..."
bun install || npm install

echo "✅ Setup complete!"
echo ""
echo "To start the development server:"
echo "  cd frontend"
echo "  bun run dev"
echo ""
echo "Or use Docker:"
echo "  docker compose up --build"
echo ""
echo "The app will be available at:"
echo "  Frontend: http://localhost:3000 (Docker) or http://localhost:5173 (local)"
echo "  API: http://localhost:5000"
