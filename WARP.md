# WARP.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

## Overview

This is a WebGPU experimental repository focused on testing advanced GPU features, particularly half-precision floating-point (f16) operations and subgroup matrix operations. The repository contains HTML files with embedded JavaScript that demonstrate various WebGPU compute shaders and matrix multiplication implementations.

## Project Structure

The repository consists of:
- **HTML demo files**: Self-contained WebGPU experiments with embedded shaders
- **Python HTTP server**: Custom server for serving HTML files during development
- **Build tools**: ESLint configuration for code quality

### Key Files

- `main.html` - Basic WebGPU f16 feature detection
- `f16.html` - Large-scale f16 matrix multiplication (1024x1024) with CPU validation
- `subgroup.html` - Basic 8x8 subgroup matrix operations
- `subgroup_tiled.html` - Tiled 16x16 matrix multiplication with subgroups
- `subgroup_tiled_smem.html` - Advanced 64x64 tiled matrix multiplication
- `main.py` - Custom HTTP server for development

## Development Commands

### Start Development Server
```bash
python main.py
# Starts server on port 8001 by default
# Access at http://localhost:8001
```

**Alternative server options:**
```bash
python main.py -p 8080                    # Custom port
python main.py -d /path/to/files          # Custom directory
python main.py --host 0.0.0.0 -p 8000     # Accessible from network
```

### Code Quality & Linting
```bash
npx eslint .                    # Lint all files
npx eslint *.html               # Lint HTML files specifically
npx prettier --write .          # Format code
```

### Python Environment Setup
```bash
# Using uv (preferred)
uv sync                         # Install dependencies
uv run python main.py          # Run server with uv

# Traditional approach
pip install -r requirements.txt  # If requirements.txt exists
python main.py
```

## Architecture Overview

### WebGPU Experimental Design

The codebase follows a progressive complexity pattern for WebGPU experiments:

1. **Feature Detection Layer** (`main.html`)
   - Tests WebGPU availability and f16 support
   - Logs adapter capabilities

2. **Basic Compute Operations** (`f16.html`)
   - Implements naive matrix multiplication in f16
   - Validates GPU results against CPU reference
   - Measures performance differences

3. **Subgroup Operations** (`subgroup.html`, `subgroup_tiled.html`, `subgroup_tiled_smem.html`)
   - Progressive complexity: 8x8 → 16x16 → 64x64 matrices
   - Uses experimental `chromium_experimental_subgroup_matrix` feature
   - Implements tiled matrix multiplication for large matrices

### Shader Architecture Patterns

**Common Pattern in All Experiments:**
```javascript
// 1. Feature detection
const requiredFeatures = ["shader-f16", "chromium-experimental-subgroup-matrix"];

// 2. Buffer setup (A, B, C matrices + staging buffer)
// 3. Shader module creation
// 4. Compute pipeline setup
// 5. Bind group configuration
// 6. Command encoding and submission
// 7. Result validation against CPU implementation
```

### HTTP Server Architecture

The custom Python server (`main.py`) provides:
- **Security**: Directory traversal protection
- **HTML-only serving**: Restricts access to .html/.htm files
- **Index generation**: Auto-generates file listing
- **Development features**: No-cache headers, logging
- **Graceful shutdown**: Signal handling

## WebGPU Features Used

### Required Browser Features
- `shader-f16` - Half-precision floating-point operations
- `chromium-experimental-subgroup-matrix` - Subgroup matrix operations (Chrome experimental)

### Shader Capabilities Demonstrated
- f16 matrix operations and precision validation
- Subgroup matrix load/store operations
- Tiled matrix multiplication strategies
- Performance comparison with CPU implementations

## Development Workflow

1. **Start the server**: `python main.py`
2. **Open browser**: Navigate to `http://localhost:8001`
3. **Select experiment**: Choose from the auto-generated index
4. **Check console**: Monitor both page output and browser dev tools
5. **Modify shaders**: Edit HTML files and refresh to test changes

### Debugging GPU Shaders

- **Browser compatibility**: Requires Chrome/Chromium with experimental WebGPU features
- **Feature detection**: All experiments include proper feature availability checks
- **Error handling**: Comprehensive error reporting for unsupported features
- **Validation**: CPU reference implementations for correctness verification

## Performance Testing

Each experiment includes:
- **Warmup runs**: To ensure accurate GPU timing
- **CPU vs GPU comparison**: Performance and accuracy validation
- **MSE/RMSE calculation**: Numerical accuracy metrics
- **Matrix size scaling**: Different complexity levels across experiments

## Notes for Development

- **Experimental features**: The subgroup matrix operations require Chrome with experimental WebGPU features enabled
- **f16 precision**: Experiments include tolerance-based validation due to half-precision limitations
- **Matrix layouts**: All experiments use row-major layout with configurable strides
- **Workgroup sizing**: Carefully tuned for different matrix sizes and GPU architectures
