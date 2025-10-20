#!/bin/bash
# Build script for OPC-UA Client Plugin

set -e

echo "Building OPC-UA Client Plugin..."

PLUGIN_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BUILD_DIR="$PLUGIN_DIR/Build"

# Create build directory
mkdir -p "$BUILD_DIR"
cd "$BUILD_DIR"

# Configure with CMake
echo "Configuring with CMake..."
cmake ..

# Build
echo "Building..."
cmake --build . --config Release

echo "Build complete!"
echo "Plugin library is in: $BUILD_DIR"
