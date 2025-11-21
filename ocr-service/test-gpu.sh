#!/bin/bash

echo "==================================="
echo "GPU Configuration Test"
echo "==================================="
echo ""

# Test 1: NVIDIA Driver
echo "1. Testing NVIDIA Driver..."
if command -v nvidia-smi &> /dev/null; then
    echo "   ✓ nvidia-smi found"
    nvidia-smi --query-gpu=driver_version --format=csv,noheader
    echo ""
else
    echo "   ✗ nvidia-smi not found"
    echo "   Please install NVIDIA drivers"
    exit 1
fi

# Test 2: GPU Information
echo "2. GPU Information:"
nvidia-smi --query-gpu=index,name,compute_cap,memory.total,memory.free --format=csv
echo ""

# Test 3: CUDA
echo "3. Testing CUDA..."
if [ -d "/usr/local/cuda" ]; then
    echo "   ✓ CUDA found at /usr/local/cuda"
    if [ -f "/usr/local/cuda/version.txt" ]; then
        cat /usr/local/cuda/version.txt
    fi
else
    echo "   ! CUDA not found at default location"
fi
echo ""

# Test 4: PaddlePaddle GPU
echo "4. Testing PaddlePaddle GPU support..."
if [ -d "venv" ]; then
    source venv/bin/activate

    python3 << 'EOF'
import sys
try:
    import paddle
    print(f"   ✓ PaddlePaddle version: {paddle.__version__}")

    # Check GPU availability
    if paddle.device.cuda.device_count() > 0:
        print(f"   ✓ GPU devices detected: {paddle.device.cuda.device_count()}")

        # Get GPU info
        for i in range(paddle.device.cuda.device_count()):
            props = paddle.device.cuda.get_device_properties(i)
            total_mem = props.total_memory / (1024**3)  # Convert to GB
            print(f"   ✓ GPU {i}: {props.name}")
            print(f"      - Total Memory: {total_mem:.2f} GB")
            print(f"      - Compute Capability: {props.major}.{props.minor}")
    else:
        print("   ✗ No GPU devices detected by PaddlePaddle")
        sys.exit(1)

except ImportError:
    print("   ✗ PaddlePaddle not installed")
    print("   Please run: cd ocr-service && ./setup.sh")
    sys.exit(1)
except Exception as e:
    print(f"   ✗ Error: {e}")
    sys.exit(1)
EOF

    if [ $? -eq 0 ]; then
        echo ""
        echo "   ✓ PaddlePaddle GPU test passed"
    else
        echo ""
        echo "   ✗ PaddlePaddle GPU test failed"
        exit 1
    fi
else
    echo "   ✗ Virtual environment not found"
    echo "   Please run: cd ocr-service && ./setup.sh"
    exit 1
fi

echo ""
echo "==================================="
echo "GPU Configuration: ✓ ALL TESTS PASSED"
echo "==================================="
echo ""
echo "Your system is ready to use GPU acceleration!"
echo ""
echo "Memory Configuration:"
echo "  - Recommended FLAGS_fraction_of_gpu_memory_to_use: 0.5"
echo "  - Recommended gpu_mem: 4000 (4GB)"
echo ""
echo "Start OCR service with: ./start.sh"
