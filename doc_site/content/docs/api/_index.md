---
title: API Documentation
type: docs
weight: 50
prev: docs/best-practices
next: docs/developer-guide
sidebar:
  open: false
---


## Configuration & Execution
- [Executor](./executor)
  - The main interface for experiment pipeline

## Pipeline Components
- [Loader](./loader)
  - Data loading and handling
- [Splitter](./splitter)
  - Data splitting for experiments
- [Processor](./processor)
  - Data preprocessing and postprocessing
  - Appx.: Available Process type
- [Synthesizer](./synthesizer)
  - Synthetic data generation
- [Constrainer](./constrainer)
  - Data constraint handler for synthetic data
- [Evaluator](./evaluator)
  - Privacy, fidelity, and utility assessment
  - Appx.: Available Evaluation Methods.
- [Reporter](./reporter)
  - Results export and reporting

## Data Management
- [Metadata](./metadata)
  - Dataset schema and properties
- [Describer](./describer)
  - Descriptive data summary