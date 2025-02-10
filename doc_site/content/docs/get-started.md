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

## Framework Structure

PETsARD follows this workflow:

1. `Loader`: Loads data from files or benchmark datasets
2. `Splitter`: Splits data into training/validation sets (optional)
3. `Preprocessor`: Prepares data for synthesis (e.g., encoding categorical values)
4. `Synthesizer`: Creates privacy-enhanced synthetic data
5. `Postprocessor`: Formats synthetic data back to original structure
6. `Evaluator`: Measures synthesis quality and privacy metrics
7. `Describer`: Generates dataset statistics and insights
8. `Reporter`: Saves results and generates reports

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