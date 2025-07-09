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

If you have the PETsARD source code locally, you can use the development environment:

```bash
# Clone the repository (if not already done)
git clone https://github.com/nics-tw/petsard.git
cd petsard

# Start development environment with Jupyter Lab
./scripts/dev-docker.sh up

# Access Jupyter Lab at http://localhost:8888
```

### Run with Your Data

```bash
# Using pre-built container
docker run -it --rm \
  -v $(pwd)/data:/workspace/data \
  -v $(pwd)/output:/workspace/output \
  ghcr.io/nics-tw/petsard:latest \
  bash

# Using local development environment
./scripts/dev-docker.sh up
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
  python -m petsard.executor demo/use-cases/data-constraining.yaml
```

### Interactive Development

```bash
# Start interactive session
docker run -it --rm \
  -v $(pwd):/workspace \
  -w /workspace \
  ghcr.io/nics-tw/petsard:latest \
  bash

# Inside container, you can run:
python -c "import petsard; print('PETsARD is ready!')"
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

If you're working with the PETsARD source code, you can use the built-in development environment management script:

### Available Commands

```bash
# Start development environment (includes Jupyter Lab)
./scripts/dev-docker.sh up

# Stop development environment
./scripts/dev-docker.sh down

# Build development image
./scripts/dev-docker.sh build

# Access container shell
./scripts/dev-docker.sh shell

# Run tests in container
./scripts/dev-docker.sh test

# View container logs
./scripts/dev-docker.sh logs

# Clean up containers and images
./scripts/dev-docker.sh clean
```

### Production vs Development Mode

```bash
# Development mode (default) - includes Jupyter Lab and dev tools
./scripts/dev-docker.sh build
./scripts/dev-docker.sh up

# Production mode - minimal runtime environment
./scripts/dev-docker.sh prod build
./scripts/dev-docker.sh prod up
```

### Development Features

- **Jupyter Lab**: Available at http://localhost:8888
- **Live Code Reloading**: Changes in source code are immediately reflected
- **Complete Development Stack**: Includes testing, documentation, and development tools
- **Volume Mounting**: Your local files are mounted into the container

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