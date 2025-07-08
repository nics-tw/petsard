---
title: Using Docker
type: docs
weight: 10
prev: docs/tutorial/external-synthesis-default-evaluation
next: docs/tutorial/use-cases
---

PETsARD provides pre-built Docker containers for easy deployment and usage. This guide shows you how to get started with Docker containers from GitHub Container Registry.

## Quick Start

### Pull and Run Container

```bash
# Pull the latest version
docker pull ghcr.io/nics-tw/petsard:latest

# Run interactive container
docker run -it --rm ghcr.io/nics-tw/petsard:latest
```

### Run with Your Data

```bash
# Mount your data directory and run
docker run -it --rm \
  -v $(pwd)/data:/workspace/data \
  -v $(pwd)/output:/workspace/output \
  ghcr.io/nics-tw/petsard:latest \
  bash
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