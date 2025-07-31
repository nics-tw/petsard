---
title: Using Docker
type: docs
weight: 10
prev: docs/tutorial/external-synthesis-default-evaluation
next: docs/tutorial/use-cases
---

PETsARD provides both pre-built Docker containers and local development environments. This guide shows you how to get started with Docker containers.

## Quick Start

### Option 1: Pre-built Containers (Recommended for Users)

```bash
# Pull the latest version
docker pull ghcr.io/nics-tw/petsard:latest

# Run interactive container
docker run -it --rm ghcr.io/nics-tw/petsard:latest
```

### Option 2: Local Development Environment

If you have the PETsARD source code locally, you can build and run containers:

```bash
# Clone the repository (if not already done)
git clone https://github.com/nics-tw/petsard.git
cd petsard

# Build standard version (default - without Jupyter)
docker build -t petsard:latest .

# Build and run Jupyter version with Jupyter Lab
docker build --build-arg INCLUDE_JUPYTER=true -t petsard:jupyter .
docker run -it -p 8888:8888 \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/notebooks:/app/notebooks \
  petsard:jupyter

# Access Jupyter Lab at http://localhost:8888
```

### Run with Your Data

```bash
# Using pre-built container (standard version)
docker run -it --entrypoint /opt/venv/bin/python3 \
  -v $(pwd):/app/data \
  ghcr.io/nics-tw/petsard:latest

# Using local Jupyter environment
docker build --build-arg INCLUDE_JUPYTER=true -t petsard:jupyter .
docker run -it -p 8888:8888 \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/notebooks:/app/notebooks \
  petsard:jupyter
# Then access Jupyter Lab at http://localhost:8888
```

## Available Tags

- `latest` - Latest stable version (from main branch)
- `dev` - Development version (from dev branch)  
- `v1.4.0` - Specific version tags
- `1.4` - Major.minor version
- `1` - Major version

## Running Examples

### Execute Configuration File

```bash
# Run a specific YAML configuration
docker run -it --rm \
  -v $(pwd):/workspace \
  -w /workspace \
  ghcr.io/nics-tw/petsard:latest \
  python -m petsard.executor demo/tutorial/use-cases/data-constraining.yaml
```

### Interactive Development

```bash
# Start interactive Python session
docker run -it --entrypoint /opt/venv/bin/python3 \
  -v $(pwd):/app/data \
  ghcr.io/nics-tw/petsard:latest

# Inside container, you can run:
# import petsard
# print('PETsARD is ready!')
```

### Batch Processing

```bash
# Process multiple configuration files
docker run -it --rm \
  -v $(pwd)/configs:/app/configs \
  -v $(pwd)/output:/app/output \
  ghcr.io/nics-tw/petsard:latest \
  bash -c "
    for config in /app/configs/*.yaml; do
      echo \"Processing \$config\"
      python -m petsard.executor \"\$config\"
    done
  "
```

## Local Development Environment Management

If you're working with the PETsARD source code, you can build and manage containers directly:

### Available Build Options

```bash
# Build standard version (default - without Jupyter)
docker build -t petsard:latest .

# Build Jupyter version (includes Jupyter Lab)
docker build --build-arg INCLUDE_JUPYTER=true -t petsard:jupyter .

# For ARM64 platforms (Apple Silicon)
docker buildx build --platform linux/arm64 --load --build-arg INCLUDE_JUPYTER=true -t petsard:jupyter --no-cache .
```

### Running Different Variants

```bash
# Run Jupyter version with Jupyter Lab
docker run -it -p 8888:8888 \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/notebooks:/app/notebooks \
  petsard:jupyter

# Run standard version Python REPL
docker run -it --entrypoint /opt/venv/bin/python3 \
  -v $(pwd):/app/data \
  petsard:latest

# Run Jupyter container in Python REPL mode
docker run -it --entrypoint /opt/venv/bin/python3 petsard:jupyter
```

### Jupyter vs Standard Mode

```bash
# Jupyter mode - includes Jupyter Lab and development tools
docker build --build-arg INCLUDE_JUPYTER=true -t petsard:jupyter .
docker run -it -p 8888:8888 \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/notebooks:/app/notebooks \
  petsard:jupyter

# Standard mode - minimal runtime environment (default)
docker build -t petsard:latest .
docker run -it --entrypoint /opt/venv/bin/python3 \
  -v $(pwd):/app/data \
  petsard:latest
```

### Development Features

- **Jupyter Lab**: Available at http://localhost:8888 (when using Jupyter variant)
- **Live Code Reloading**: Changes in source code are immediately reflected through volume mounting
- **Complete Development Stack**: Includes dependencies from pyproject.toml [docker] group
- **Volume Mounting**: Your local files are mounted into the container for persistent development

## Environment Variables

The container supports these environment variables:

- `PYTHONPATH` - Python module search path (default: `/app`)
- `PYTHONUNBUFFERED` - Disable Python output buffering (default: `1`)
- `PYTHONDONTWRITEBYTECODE` - Prevent .pyc file generation (default: `1`)

```bash
# Set custom environment variables
docker run -it --rm \
  -e PYTHONPATH=/workspace:/app \
  -v $(pwd):/workspace \
  ghcr.io/nics-tw/petsard:latest \
  python your_script.py
```

## Container Directory Structure

```
/app/
├── petsard/          # PETsARD package source code
├── demo/             # Example files
├── templates/        # Template files
├── pyproject.toml    # Project configuration
├── requirements.txt  # Dependencies list
└── README.md         # Documentation
```

## Troubleshooting

### Permission Issues

```bash
# If you encounter permission issues, specify user ID
docker run -it --rm \
  --user $(id -u):$(id -g) \
  -v $(pwd):/workspace \
  ghcr.io/nics-tw/petsard:latest \
  bash
```

### Memory Limits

```bash
# Increase memory limit if needed
docker run -it --rm \
  --memory=4g \
  ghcr.io/nics-tw/petsard:latest
```

### Health Check

```bash
# Verify container is working correctly
docker run --rm ghcr.io/nics-tw/petsard:latest python -c "
import petsard
print('✅ PETsARD loaded successfully')
from petsard.executor import Executor
print('✅ Executor available')
"
```

## Next Steps

- Learn about [YAML Configuration](../yaml-config) for experiment setup
- Explore [Default Synthesis](../default-synthesis) examples
- Check [Use Cases](../use-cases) for practical applications