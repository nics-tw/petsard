---
title: Get Started
type: docs
weight: 2
prev: docs
next: docs/tutorial
---

## Installation

PETsARD is available on PyPI and can be installed with different dependency groups based on your needs. You can also install from source using `pyproject.toml` or `requirements.txt`.

### PyPI Installation (Recommended)

```bash
# Default installation (configuration parsing only)
pip install petsard

# Data science features (recommended for most users)
pip install petsard[ds]

# Complete installation with development tools
pip install petsard[all]

# Development tools only
pip install petsard[dev]
```

### Installation Options

| Group | Command | Included Features |
|-------|---------|-------------------|
| **Default** | `pip install petsard` | Core functionality: configuration, data loading, synthesis, evaluation (pyyaml, pandas, anonymeter, sdmetrics, sdv, torch, etc.) |
| **Data Science** | `pip install petsard[ds]` | Basic functionality + Jupyter Notebook support (ipykernel, jupyterlab, notebook, etc.) |
| **Complete** | `pip install petsard[all]` | Data science functionality + extended support (benchmark datasets, Excel file support) |
| **Development** | `pip install petsard[dev-tools]` | Testing and development utilities (pytest, ruff, coverage, etc.) |

### Source Installation

For development or custom builds:

```bash
# Clone the repository
git clone https://github.com/nics-tw/petsard.git
cd petsard

# Install with pyproject.toml
pip install -e ".[all]"

# Or install with requirements.txt (based on default)
pip install -r requirements.txt
```

**Recommended tools for development:**
* `pyenv` - Python version management
* `poetry` / `uv` - Package management

### Offline Environment Preparation

For environments without internet access, we provide a wheel downloader tool to prepare all dependencies in advance:

```bash
# Download core dependencies only
python demo/petsard_wheel_downloader.py --branch main --python-version 3.11 --os linux

# Download with additional dependency groups
python demo/petsard_wheel_downloader.py --branch main --python-version 3.11 --os linux --groups ds
```

**Parameter descriptions:**
- `--branch`: Git branch name (e.g., main, dev)
- `--python-version`: Python version (e.g., 3.10, 3.11, 3.11.5)
- `--os`: Target operating system, supports:
  - `linux`: Linux 64-bit
  - `windows`: Windows 64-bit
  - `macos`: macOS Intel
  - `macos-arm`: macOS Apple Silicon
- `--groups`: Optional dependency groups (can specify multiple groups separated by spaces)

## Quick Start

PETsARD is a privacy-enhancing data synthesis and evaluation framework. To start using PETsARD:

1. Create a minimal YAML configuration file:
   ```yaml
   # config.yaml
   Loader:
       demo:
           method: 'default'  # Uses Adult Income dataset
   Synthesizer:
       demo:
           method: 'default'  # Uses SDV Gaussian Copula
   Reporter:
       output:
           method: 'save_data'
           output: 'result'
           source: 'Synthesizer'
   ```

2. Run with two lines of code:
   ```python
   from petsard import Executor


   exec = Executor(config='config.yaml')
   exec.run()
   ```

## Basic Configuration

Here's a simple example that demonstrates the complete workflow of PETsARD. This configuration will:

1. Loads the Adult Income demo dataset
2. Automatically determines data types and applies appropriate preprocessing
3. Generates synthetic data using SDV's Gaussian Copula method
4. Evaluates basic quality metrics and privacy measures using SDMetrics
5. Saves both synthetic data and evaluation report

```yaml
Loader:
    demo:
        method: 'default'
Preprocessor:
    demo:
        method: 'default'
Synthesizer:
    demo:
        method: 'default'
Postprocessor:
    demo:
        method: 'default'
Evaluator:
    demo:
        method: 'default'
Reporter:
    save_data:
        method: 'save_data'
        output: 'demo_result'
        source: 'Postprocessor'
    save_report:
        method: 'save_report'
        output: 'demo_report'
        eval: 'demo'
        granularity: 'global'
```

## Next Steps

* Check the Tutorial section for detailed examples
* Visit the API Documentation for complete module references
* Explore benchmark datasets for testing
* Review example configurations in the GitHub repository