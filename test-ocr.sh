#!/bin/bash

# Test OCR Service Script

set -e

echo "Testing OCR Microservice"
echo "========================"
echo ""

# Check if OCR service is running
echo "1. Checking if OCR service is running..."
if curl -s http://localhost:8119/health > /dev/null 2>&1; then
    echo "   ✓ OCR service is running"
else
    echo "   ✗ OCR service is not running"
    echo ""
    echo "Please start the OCR service first:"
    echo "   cd ocr-service"
    echo "   ./start.sh"
    exit 1
fi

echo ""

# Test with provided image
if [ -f "$1" ]; then
    echo "2. Testing OCR with image: $1"
    echo ""

    # Call OCR service
    response=$(curl -s -X POST http://localhost:8119/ocr -F "file=@$1")

    # Check if successful
    if echo "$response" | grep -q '"success":true'; then
        echo "   ✓ OCR processing successful!"
        echo ""
        echo "Extracted Text:"
        echo "==============="
        echo "$response" | python3 -c "import sys, json; print(json.load(sys.stdin)['text'])"
        echo ""
        echo ""
        echo "Full Response (JSON):"
        echo "===================="
        echo "$response" | python3 -m json.tool
    else
        echo "   ✗ OCR processing failed"
        echo ""
        echo "Error:"
        echo "$response" | python3 -m json.tool
    fi
else
    echo "Usage: $0 <image-file>"
    echo ""
    echo "Example:"
    echo "  $0 /path/to/image.png"
fi

echo ""
