---
title: Docker Development
type: docs
weight: 89
prev: docs/developer-guide/test-coverage
next: docs/developer-guide
---

This guide covers Docker development setup, testing, and deployment for PETsARD developers.

## Development Environment Setup

### Prerequisites

- Docker Desktop installed and running
- Git repository cloned locally
- Basic understanding of Docker concepts

### Quick Environment Check

Verify your Docker setup with basic commands:

```bash
# Check Docker installation and version
docker --version

# Check Docker daemon status
docker info

# Test basic Docker functionality
docker run --rm hello-world
```

This will:
- Verify Docker version
- Check Docker daemon status
- Test basic Docker functionality

## Local Development with Docker

### Building Local Images

```bash
# Build standard version (default - without Jupyter)
docker build -t petsard:latest .

# Build Jupyter version with Jupyter Lab
docker build --build-arg INCLUDE_JUPYTER=true -t petsard:jupyter .

# For ARM64 platforms (Apple Silicon)
docker buildx build --platform linux/arm64 --load --build-arg INCLUDE_JUPYTER=true -t petsard:jupyter --no-cache .
```

### Running Containers

#### Standard Container

```bash
# Run standard container (without Jupyter) - Python REPL
docker run -it --entrypoint /opt/venv/bin/python3 petsard:standard

# Run with volume mounts for data
docker run -it -v $(pwd):/app/data --entrypoint /opt/venv/bin/python3 petsard:standard
```

#### Jupyter Lab Container

```bash
# Run container with Jupyter Lab (default behavior)
docker run -it -p 8888:8888 \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/notebooks:/app/notebooks \
  petsard:jupyter

# Run Python REPL in Jupyter container
docker run -it --entrypoint /opt/venv/bin/python3 petsard:jupyter

# Access Jupyter Lab at http://localhost:8888
```

**Features:**
- Jupyter Lab interface for interactive development
- Port 8888 exposed for browser access
- Volume mounting for persistent data and notebooks
- ARM64 optimization for Apple Silicon

## Development Environment Management

### Docker Build Variants

PETsARD provides flexible Docker builds with optional Jupyter Lab support:

```bash
# Build Jupyter version (with Jupyter Lab)
docker build --build-arg INCLUDE_JUPYTER=true -t petsard:jupyter .

# Build standard version (without Jupyter)
docker build --build-arg INCLUDE_JUPYTER=false -t petsard:standard .

# Default build (includes Jupyter)
docker build -t petsard:latest .
```

### Jupyter vs Standard Environments

#### Jupyter Environment Features

- **Jupyter Lab Integration** - Full Jupyter environment accessible at http://localhost:8888
- **Interactive Development** - Volume mounts for real-time development
- **Complete Development Stack** - All dependencies from pyproject.toml [docker] group
- **Larger Image Size** - Includes Jupyter Lab and development tools

```bash
# Run Jupyter container with Jupyter Lab
docker run -it --rm \
  -p 8888:8888 \
  -v $(pwd):/workspace \
  petsard:jupyter
# Access Jupyter Lab at http://localhost:8888
```

#### Standard Environment Features

- **Core Runtime** - Only essential dependencies for PETsARD core functionality
- **Smaller Image Size** - Optimized for deployment without Jupyter
- **Security Optimized** - Non-root user execution (UID 1000)
- **Distroless Base** - Minimal attack surface using gcr.io/distroless/python3

```bash
# Run standard container
docker run -it --rm \
  -v $(pwd)/data:/app/data \
  petsard:standard
```

### Configuration Files

The Docker environment uses these key files:

- **`Dockerfile`** - Multi-stage production-optimized image with optional Jupyter support
- **`pyproject.toml`** - Project configuration with dependency groups
- **`.github/workflows/docker-publish.yml`** - CI/CD pipeline for automated builds

### Environment Variables

The container automatically configures:

```bash
# Python optimization
PYTHONPATH=/app
PYTHONUNBUFFERED=1
PYTHONDONTWRITEBYTECODE=1

# Performance optimization
TORCH_DISABLE_DISTRIBUTED=1
OMP_NUM_THREADS=1

# Jupyter configuration
HOME=/app
JUPYTER_CONFIG_DIR=/app/.jupyter
JUPYTER_DATA_DIR=/app/.local/share/jupyter

# Build variant indicator
INCLUDE_JUPYTER=true/false
```

## Development Workflows

### Feature Development

1. **Setup Development Environment**
   ```bash
   # Build Jupyter image with Jupyter Lab (ARM64 optimized)
   docker buildx build --platform linux/arm64 --load --build-arg INCLUDE_JUPYTER=true -t petsard:jupyter --no-cache .
   
   # Start container with Jupyter Lab
   docker run -it -p 8888:8888 \
     -v $(pwd)/data:/app/data \
     -v $(pwd)/notebooks:/app/notebooks \
     petsard:jupyter
   
   # Access Jupyter Lab at http://localhost:8888
   ```

2. **Code and Test**
   ```bash
   # Run Python REPL for testing
   docker run -it --entrypoint /opt/venv/bin/python3 petsard:jupyter
   
   # Run with data volume for testing
   docker run -it -v $(pwd):/app/data --entrypoint /opt/venv/bin/python3 petsard:jupyter
   
   # Test PETsARD functionality inside container
   # python -m petsard.executor demo/tutorial/use-cases/data-constraining.yaml
   ```

3. **Test Both Build Variants**
   ```bash
   # Test Jupyter build (with Jupyter Lab)
   docker build --build-arg INCLUDE_JUPYTER=true -t petsard:jupyter .
   
   # Test standard build (without Jupyter)
   docker build --build-arg INCLUDE_JUPYTER=false -t petsard:standard .
   
   # For ARM64 platforms
   docker buildx build --platform linux/arm64 --load --build-arg INCLUDE_JUPYTER=true -t petsard:jupyter --no-cache .
   ```

### Research and Experimentation Workflow

1. **Start Jupyter Environment**
   ```bash
   # Run container with Jupyter Lab
   docker run -it --rm \
     -p 8888:8888 \
     -v $(pwd):/workspace \
     petsard:jupyter
   # Navigate to http://localhost:8888
   ```

2. **Create and Run Notebooks**
   - Use the `/workspace` directory for persistent notebooks
   - Access PETsARD modules directly: `import petsard`
   - Experiment with different configurations

3. **Export Results**
   ```bash
   # Access container shell for file operations
   docker run -it --rm \
     -v $(pwd):/workspace \
     petsard:jupyter \
     bash
   # Your notebooks and data persist in mounted volumes
   ```

## Testing and Validation

### Manual Testing Commands

```bash
# Test basic functionality (default includes Jupyter)
docker run --rm petsard:latest python -c "
import petsard
import importlib.metadata
print(f'✅ PETsARD v{importlib.metadata.version(\"petsard\")} loaded')
from petsard.executor import Executor
print('✅ All modules imported successfully')
"

# Test with demo configuration
docker run --rm \
  -v $(pwd):/workspace \
  -w /workspace \
  petsard:latest \
  python -m petsard.executor demo/tutorial/use-cases/data-constraining.yaml

# Test Jupyter variant
docker run --rm \
  -p 8888:8888 \
  -v $(pwd):/workspace \
  petsard:jupyter \
  python -c "import jupyterlab; print('✅ Jupyter Lab available')"

# Test standard variant
docker run --rm \
  petsard:standard \
  python -c "import petsard; print('✅ Standard build OK')"
```

### Build Testing

```bash
# Test standard build (without Jupyter)
docker build --build-arg INCLUDE_JUPYTER=false -t petsard:test-standard .
docker run --rm petsard:test-standard python -c "import petsard; print('✅ Standard build OK')"

# Test Jupyter build (with Jupyter Lab)
docker build --build-arg INCLUDE_JUPYTER=true -t petsard:test-jupyter .
docker run --rm petsard:test-jupyter python -c "import jupyterlab; print('✅ Jupyter build OK')"

# Clean up test images
docker rmi petsard:test-standard petsard:test-jupyter
```

## Multi-Stage Dockerfile Architecture

The Dockerfile uses a multi-stage build for optimization:

### Builder Stage
- Based on `python:3.11-slim`
- Installs build dependencies and compilation tools
- Builds virtual environment in `/opt/venv`
- **ARM64 Optimization** - Special handling for Apple Silicon with CPU-only PyTorch
- Installs PETsARD with dependencies based on `INCLUDE_JUPYTER` build argument
- Uses `--dependency-groups=docker` for Jupyter Lab installation

### Production Stage
- Based on `python:3.11-slim` (not distroless for better compatibility)
- Creates dedicated `petsard` user for security
- Copies virtual environment and application files from builder
- Adaptive entrypoint script that handles both Jupyter and Python REPL modes
- **ARM64 Performance Tuning** - Optimized environment variables for Apple Silicon

### Key Features
- **Python 3.11** - Stable Python version with anonymeter compatibility
- **Virtual Environment Isolation** - Dependencies isolated in `/opt/venv`
- **ARM64 Optimization** - Special CPU-only PyTorch installation for Apple Silicon
- **Conditional Jupyter** - Optional Jupyter Lab based on build argument
- **Non-root Execution** - Runs as dedicated `petsard` user for security
- **Cross-platform Support** - Optimized for both x86_64 and ARM64 architectures

## CI/CD Integration

### Automated Building

The project uses GitHub Actions for automated Docker building:

```yaml
# Triggered by semantic release completion
workflow_run:
  workflows: ["Semantic Release"]
  types: [completed]
  branches: [main, dev]
```

### Version Management

- **Semantic Release Integration** - Version numbers managed automatically
- **Dynamic Tagging** - Multiple tags created per release:
  - `latest` (main branch)
  - `v1.4.0` (specific version)
  - `1.4` (major.minor)
  - `1` (major version)

### Registry Publishing

Images are published to GitHub Container Registry:
- `ghcr.io/nics-tw/petsard:latest`
- `ghcr.io/nics-tw/petsard:v1.4.0`

## Debugging Issues

### Check Container Logs

```bash
# Check logs for running container
docker logs <container_id>

# Follow logs in real-time
docker logs -f <container_id>
```

### Interactive Debugging

```bash
# Start container with debugging access
docker run -it --rm \
  -v $(pwd):/workspace \
  petsard:jupyter \
  bash

# Debug standard version
docker run -it --rm \
  -v $(pwd):/workspace \
  petsard:standard \
  python
```

### Health Check Debugging

```bash
# Manual health check
docker run --rm petsard:latest python -c "
import importlib.metadata
try:
    version = importlib.metadata.version('petsard')
    print(f'✅ Health check passed - PETsARD v{version}')
except Exception as e:
    print(f'❌ Health check failed: {e}')
"
```

## Performance Optimization

### Build Optimization

- **Layer Caching** - Dockerfile optimized for Docker layer caching
- **Multi-stage Builds** - Smaller final images
- **Dependency Caching** - Requirements installed before code copy

### Runtime Optimization

- **Virtual Environment** - Isolated Python environment
- **Minimal Base Image** - `python:3.11-slim` for smaller footprint
- **Non-root Execution** - Security and permission optimization

## Troubleshooting

### Common Issues

1. **Build Failures**
   ```bash
   # Clean build without cache
   docker build --no-cache -t petsard:debug .
   ```

2. **Permission Issues**
   ```bash
   # Fix file permissions
   docker run --rm -v $(pwd):/workspace \
     --user $(id -u):$(id -g) \
     petsard:dev chown -R $(id -u):$(id -g) /workspace
   ```

3. **Memory Issues**
   ```bash
   # Increase Docker memory limit
   docker run --memory=4g petsard:dev
   ```

### Environment Variables

Key environment variables used in containers:

```bash
# Python optimization
PYTHONPATH=/app
PYTHONUNBUFFERED=1
PYTHONDONTWRITEBYTECODE=1

# Jupyter-specific (when INCLUDE_JUPYTER=true)
JUPYTER_ENABLE_LAB=yes
JUPYTER_ALLOW_ROOT=1

# Build variant indicator
INCLUDE_JUPYTER=true/false
```

## Best Practices

1. **Use Docker Compose** for development workflows
2. **Test locally** before pushing changes
3. **Monitor image sizes** to keep them minimal
4. **Use health checks** for production deployments
5. **Follow semantic versioning** for image tags
6. **Document environment variables** and configuration options

## Security Considerations

- **Non-root user** execution in production
- **Minimal attack surface** with slim base images
- **No hardcoded secrets** in Dockerfile
- **Regular base image updates** for security patches