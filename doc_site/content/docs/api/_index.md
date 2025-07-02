---
title: API Documentation
type: docs
weight: 50
prev: docs/best-practices
next: docs/developer-guide
sidebar:
  open: false
---


## API Reference Overview

| Module | Object Name | Creation Method | Main Methods |
|--------|-------------|-----------------|--------------|
| [Executor](./executor) | `Executor` | `Executor(config)` | `run()`, `get_result()`, `get_timing()` |
| [Loader](./loader) | `Loader` | `Loader(filepath, **kwargs)` | `load()` |
| [Metadater](./metadater) | `Metadater` | `Metadater.create_schema()` | `create_schema()`, `validate_schema()` |
| [Splitter](./splitter) | `Splitter` | `Splitter(**kwargs)` | `split()` |
| [Processor](./processor) | `Processor` | `Processor(metadata, config)` | `fit()`, `transform()`, `inverse_transform()` |
| [Synthesizer](./synthesizer) | `Synthesizer` | `Synthesizer(**kwargs)` | `create()`, `fit_sample()` |
| [Constrainer](./constrainer) | `Constrainer` | `Constrainer(config)` | `apply()`, `resample_until_satisfy()` |
| [Evaluator](./evaluator) | `Evaluator` | `Evaluator(**kwargs)` | `create()`, `eval()` |
| [Describer](./describer) | `Describer` | `Describer(**kwargs)` | `create()`, `eval()` |
| [Reporter](./reporter) | `Reporter` | `Reporter(method, **kwargs)` | `create()`, `report()` |
| [Operator](./operator) | `*Operator` | `*Operator(config)` | `run()`, `set_input()`, `get_result()` |
| [Config](./config) | `Config` | `Config(config_dict)` | Auto-processing during init |
| [Status](./status) | `Status` | `Status(config)` | `put()`, `get_result()`, `create_snapshot()` |
| [Utils](./utils) | Functions | Direct import | `load_external_module()` |

## Configuration & Execution
- [Executor](./executor) - The main interface for experiment pipeline

## Data Management
- [Metadater](./metadater) - Dataset schema and metadata management

## Pipeline Components
- [Loader](./loader) - Data loading and handling
- [Splitter](./splitter) - Data splitting for experiments
- [Processor](./processor) - Data preprocessing and postprocessing
- [Synthesizer](./synthesizer) - Synthetic data generation
- [Constrainer](./constrainer) - Data constraint handler for synthetic data
- [Evaluator](./evaluator) - Privacy, fidelity, and utility assessment
- [Describer](./describer) - Descriptive data summary
- [Reporter](./reporter) - Results export and reporting

## System Components
- [Operator](./operator) - Standardized execution wrappers for all modules
- [Config](./config) - Experiment configuration management
- [Status](./status) - Pipeline state and progress tracking
- [Utils](./utils) - Core utility functions and external module loading