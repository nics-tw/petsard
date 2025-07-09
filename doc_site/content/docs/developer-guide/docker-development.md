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

Use the provided script to verify your Docker setup:

```bash
# Check Docker installation and basic functionality
./scripts/quick-docker-test.sh
```

This script will:
- Verify Docker version
- Check Docker daemon status
- Test basic Docker functionality

## Local Development with Docker

### Building Local Images

```bash
# Build development image
docker build -t petsard:dev .

# Build with specific build arguments
docker build \
  --build-arg BUILD_DATE="$(date -u +'%Y-%m-%dT%H:%M:%SZ')" \
  --build-arg VCS_REF="$(git rev-parse --short HEAD)" \
  -t petsard:local .
```

### Docker Compose Development

The project includes a comprehensive `docker-compose.yml` with three services:

#### 1. Development Service (`petsard`)

```bash
# Start development container
docker-compose up -d petsard

# Enter the container
docker-compose exec petsard bash

# Stop the container
docker-compose down
```

**Features:**
- Mounts entire project directory to `/workspace`
- Persistent container for development
- Real-time code changes reflected in container

#### 2. Demo Service (`petsard-demo`)

```bash
# Run demo container
docker-compose up petsard-demo
```

**Features:**
- Focused on `/app/demo` directory
- Automatically lists available YAML configurations
- Lightweight for demonstration purposes

#### 3. Jupyter Service (`petsard-jupyter`)

```bash
# Start Jupyter notebook server
docker-compose up -d petsard-jupyter

# Access at http://localhost:8888
```

**Features:**
- Jupyter notebook environment
- Port 8888 exposed for browser access
- No authentication required for development

## Development Environment Management

### Unified Development Script

PETsARD provides a unified script for managing both development and production Docker environments:

```bash
# Development mode (default)
./scripts/dev-docker.sh <command>

# Production mode
./scripts/dev-docker.sh prod <command>
BUILD_TYPE=prod ./scripts/dev-docker.sh <command>
```

#### Available Commands

```bash
# Environment management
./scripts/dev-docker.sh up          # Start environment
./scripts/dev-docker.sh down        # Stop and remove environment
./scripts/dev-docker.sh build       # Build images
./scripts/dev-docker.sh shell       # Access container shell
./scripts/dev-docker.sh test        # Run tests in container
./scripts/dev-docker.sh logs        # View container logs
./scripts/dev-docker.sh clean       # Clean up images and containers
./scripts/dev-docker.sh help        # Show all available commands
```

### Development vs Production Environments

#### Development Environment Features

- **Jupyter Lab Integration** - Full Jupyter environment accessible at http://localhost:8888
- **Live Code Reloading** - Volume mounts for real-time development
- **Complete Development Stack** - All dependencies including testing and documentation tools
- **Larger Image Size** - ~1.5GB with all development tools

```bash
# Start development environment
./scripts/dev-docker.sh up
# Access Jupyter Lab at http://localhost:8888
```

#### Production Environment Features

- **Minimal Runtime** - Only essential dependencies
- **Smaller Image Size** - ~450MB optimized for deployment
- **Security Optimized** - Non-root user execution
- **Health Checks** - Built-in container health monitoring

```bash
# Build and run production environment
./scripts/dev-docker.sh prod build
./scripts/dev-docker.sh prod up
```

### Configuration Files

The development environment uses these key files:

- **`Dockerfile.dev`** - Multi-stage development image with Jupyter
- **`Dockerfile`** - Production-optimized image
- **`docker-compose.dev.yml`** - Development services configuration
- **`scripts/dev-docker.sh`** - Unified management script

### Environment Variables

Both environments automatically configure:

```bash
# Python optimization
PYTHONPATH=/app
PYTHONUNBUFFERED=1
PYTHONDONTWRITEBYTECODE=1

# Development-specific (dev mode only)
JUPYTER_ENABLE_LAB=yes
JUPYTER_TOKEN=""
JUPYTER_ALLOW_ROOT=1
PETSARD_ENV=development
```

## Development Workflows

### Feature Development with New Script

1. **Setup Development Environment**
   ```bash
   # Start development environment with Jupyter
   ./scripts/dev-docker.sh up
   
   # Access Jupyter Lab at http://localhost:8888
   # Or access container shell
   ./scripts/dev-docker.sh shell
   ```

2. **Code and Test**
   ```bash
   # Run tests in development container
   ./scripts/dev-docker.sh test
   
   # Or manually inside container
   ./scripts/dev-docker.sh shell
   python -m pytest tests/
   python -m petsard.executor demo/use-cases/data-constraining.yaml
   ```

3. **Test Both Environments**
   ```bash
   # Test development build
   ./scripts/dev-docker.sh build
   
   # Test production build
   ./scripts/dev-docker.sh prod build
   
   # Run comprehensive tests
   ./scripts/test-docker.sh
   ```

### Research and Experimentation Workflow

1. **Start Jupyter Environment**
   ```bash
   ./scripts/dev-docker.sh up
   # Navigate to http://localhost:8888
   ```

2. **Create and Run Notebooks**
   - Use the `/app/notebooks` directory for persistent notebooks
   - Access PETsARD modules directly: `import petsard`
   - Experiment with different configurations

3. **Export Results**
   ```bash
   # Access container to export results
   ./scripts/dev-docker.sh shell
   # Your notebooks and data persist in mounted volumes
   ```

## Testing and Validation

### Comprehensive Testing Script

```bash
# Run full Docker image testing
./scripts/test-docker.sh
```

This script performs:
- Docker environment validation
- Image building with error handling
- PETsARD package import testing
- Module functionality verification
- Health check validation
- Image size and metadata display

### Manual Testing Commands

```bash
# Test basic functionality
docker run --rm petsard:dev python -c "
import petsard
import importlib.metadata
print(f'✅ PETsARD v{importlib.metadata.version(\"petsard\")} loaded')
from petsard.executor import Executor
print('✅ All modules imported successfully')
"

# Test with demo configuration
docker run --rm \
  -v $(pwd)/demo:/app/demo \
  petsard:dev \
  python -m petsard.executor /app/demo/use-cases/data-constraining.yaml
```

## Multi-Stage Dockerfile Architecture

The Dockerfile uses a multi-stage build for optimization:

### Builder Stage
- Based on `python:3.11-slim`
- Installs build dependencies and compilation tools
- Uses `uv` package manager for faster dependency installation
- Builds virtual environment in `/opt/venv`
- Installs PETsARD in editable mode

### Production Stage
- Minimal runtime environment
- Copies only necessary files from builder stage
- Runs as non-root user (UID 1000) for security
- Includes health check using `importlib.metadata`

### Key Features
- **Python 3.11** - Stable Python version with anonymeter compatibility
- **Virtual Environment Isolation** - Dependencies isolated in `/opt/venv`
- **Security** - Non-root user execution
- **Health Monitoring** - Built-in health checks
- **ARM64 Support** - Compatible with Apple Silicon

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

## Development Workflows

### Feature Development

1. **Setup Development Environment**
   ```bash
   # Start development container
   docker-compose up -d petsard
   docker-compose exec petsard bash
   ```

2. **Code and Test**
   ```bash
   # Inside container - your changes are live-mounted
   python -m pytest tests/
   python -m petsard.executor demo/use-cases/data-constraining.yaml
   ```

3. **Test Docker Build**
   ```bash
   # Test local build before pushing
   ./scripts/test-docker.sh
   ```

### Debugging Issues

1. **Check Container Logs**
   ```bash
   docker logs <container_id>
   docker-compose logs petsard
   ```

2. **Interactive Debugging**
   ```bash
   # Start container with debugging tools
   docker run -it --rm \
     -v $(pwd):/workspace \
     --entrypoint bash \
     petsard:dev
   ```

3. **Health Check Debugging**
   ```bash
   # Manual health check
   docker run --rm petsard:dev python -c "
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

Key environment variables for development:

```bash
# Python optimization
PYTHONPATH=/workspace:/app
PYTHONUNBUFFERED=1
PYTHONDONTWRITEBYTECODE=1

# Development mode
PETSARD_ENV=development
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