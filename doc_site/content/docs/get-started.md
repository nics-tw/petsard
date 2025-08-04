---
title: Get Started
type: docs
weight: 2
prev: docs
next: docs/tutorial
---

## Installation

*Below we demonstrate the native Python environment setup. However, for better dependency management, we recommend using:*

**Recommended tools:**
* `pyenv` - Python version management
* `poetry` / `uv` - Package management

### Native Python Setup

1. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   # or
   venv\Scripts\activate     # Windows
   ```

2. Upgrade pip:
   ```bash
   python -m pip install --upgrade pip
   ```

3. Install required packages:
   ```bash
   pip install -r requirements.txt
   ```

### Offline Environment Preparation

For environments without internet access, we provide a wheel downloader tool to prepare all dependencies in advance:

```bash
# Download core dependencies only
python demo/petsard_wheel_downloader.py --branch main --python-version 3.11 --os linux

# Download with additional dependency groups
python demo/petsard_wheel_downloader.py --branch main --python-version 3.11 --os linux --groups pytorch jupyter
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
  - `pytorch`: PyTorch and CUDA-related packages for deep learning
  - `jupyter`: Jupyter Notebook and IPython packages for interactive development
  - `dev`: Development tools like pytest, ruff, and other utilities

**Dependency Groups Examples:**

```bash
# Download only core dependencies
python demo/petsard_wheel_downloader.py --branch main --python-version 3.11 --os linux

# Download with PyTorch support
python demo/petsard_wheel_downloader.py --branch main --python-version 3.11 --os linux --groups pytorch

# Download with Jupyter support
python demo/petsard_wheel_downloader.py --branch main --python-version 3.11 --os linux --groups jupyter

# Download with multiple groups
python demo/petsard_wheel_downloader.py --branch main --python-version 3.11 --os linux --groups pytorch jupyter

# Download with all available groups
python demo/petsard_wheel_downloader.py --branch main --python-version 3.11 --os linux --groups pytorch jupyter dev
```

This tool downloads PETsARD and all its dependency wheel files, and generates detailed installation logs.

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