#!/bin/bash

# TreeLLM Frontend Setup Script
# This script copies the frontend files and sets up the TreeLLM integrated frontend

echo "Setting up TreeLLM Frontend..."

# Source and destination directories
SOURCE_DIR="/Users/kimminjun/Desktop/frontend"
DEST_DIR="/Users/kimminjun/Desktop/TreeLLM/frontend"

# Copy necessary files and directories
echo "Copying frontend files..."

# Copy src components (except pages and Header which we've customized)
cp "$SOURCE_DIR/src/components/ContentsTree.tsx" "$DEST_DIR/src/components/" 2>/dev/null
cp "$SOURCE_DIR/src/components/EditorPanel.tsx" "$DEST_DIR/src/components/" 2>/dev/null
cp "$SOURCE_DIR/src/components/FeedbackPanel.tsx" "$DEST_DIR/src/components/" 2>/dev/null
cp "$SOURCE_DIR/src/components/FileSidebar.tsx" "$DEST_DIR/src/components/" 2>/dev/null
cp "$SOURCE_DIR/src/components/Viewer.tsx" "$DEST_DIR/src/components/" 2>/dev/null

# Copy UI components
mkdir -p "$DEST_DIR/src/components/ui"
cp -r "$SOURCE_DIR/src/components/ui/"* "$DEST_DIR/src/components/ui/" 2>/dev/null

# Copy lib directory
mkdir -p "$DEST_DIR/src/lib"
cp -r "$SOURCE_DIR/src/lib/"* "$DEST_DIR/src/lib/" 2>/dev/null

# Copy types directory
mkdir -p "$DEST_DIR/src/types"
cp -r "$SOURCE_DIR/src/types/"* "$DEST_DIR/src/types/" 2>/dev/null

# Copy styles
cp "$SOURCE_DIR/src/index.css" "$DEST_DIR/src/" 2>/dev/null

# Copy main and App files
cp "$SOURCE_DIR/src/main.tsx" "$DEST_DIR/src/" 2>/dev/null
cp "$SOURCE_DIR/src/App.tsx" "$DEST_DIR/src/" 2>/dev/null
cp "$SOURCE_DIR/src/vite-env.d.ts" "$DEST_DIR/src/" 2>/dev/null

# Copy ChatPage (not modified)
mkdir -p "$DEST_DIR/src/pages"
cp "$SOURCE_DIR/src/pages/ChatPage.tsx" "$DEST_DIR/src/pages/" 2>/dev/null

# Copy configuration files
cp "$SOURCE_DIR/index.html" "$DEST_DIR/" 2>/dev/null
cp "$SOURCE_DIR/vite.config.ts" "$DEST_DIR/" 2>/dev/null
cp "$SOURCE_DIR/tsconfig.json" "$DEST_DIR/" 2>/dev/null
cp "$SOURCE_DIR/tsconfig.app.json" "$DEST_DIR/" 2>/dev/null
cp "$SOURCE_DIR/tsconfig.node.json" "$DEST_DIR/" 2>/dev/null
cp "$SOURCE_DIR/tailwind.config.js" "$DEST_DIR/" 2>/dev/null
cp "$SOURCE_DIR/postcss.config.cjs" "$DEST_DIR/" 2>/dev/null
cp "$SOURCE_DIR/eslint.config.js" "$DEST_DIR/" 2>/dev/null
cp "$SOURCE_DIR/.gitignore" "$DEST_DIR/" 2>/dev/null

# Copy public directory
mkdir -p "$DEST_DIR/public"
cp -r "$SOURCE_DIR/public/"* "$DEST_DIR/public/" 2>/dev/null

echo "File copying completed!"

# Navigate to destination directory
cd "$DEST_DIR"

# Install dependencies
echo "Installing dependencies..."
npm install

echo "Setup completed!"
echo ""
echo "To run the TreeLLM integrated frontend:"
echo "1. Start the TreeLLM backend: cd /Users/kimminjun/Desktop/TreeLLM && python app.py"
echo "2. Start the frontend: cd /Users/kimminjun/Desktop/TreeLLM/frontend && npm run dev"
echo ""
echo "The frontend will be available at http://localhost:5173"
echo "The backend API will be running at http://localhost:5001"