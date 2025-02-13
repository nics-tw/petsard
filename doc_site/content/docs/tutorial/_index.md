---
title: Tutorial
type: docs
weight: 10
prev: docs/get-started
next: docs/best-practices
sidebar:
  open: false
---


You can run these examples by executing the following code with your YAML config file:

```python
exec = Executor(config=yaml_path)
exec.run()
```

The following scenarios guide you in choosing the right YAML configuration:

1. **YAML Configuration: [YAML Setup](./yaml-config)**

  - When you need to understand how to configure experiment parameters
  - For managing and organizing complex experiment workflows
  - Control all experiment settings through YAML files

2. **Basic Usage: [Default Synthesis](./default-synthesis)**

  - When you only need basic data synthesis
  - For simple privacy-enhanced synthetic data generation

3. **Data Constraining: [Data Constraining](./data-constraining)**

  - When you need to control synthetic data characteristics
  - Includes field value rules, field combinations, and NA handling
  - Ensure synthetic data meets business logic

4. **Basic Usage with Evaluation: [Default Synthesis and Evaluation](./default-synthesis-default-evaluation)**

  - When you need both synthesis and comprehensive evaluation
  - Includes protection, fidelity, and utility assessments

5. **Evaluation of External Solutions: [External Synthesis with Default Evaluation](./external-synthesis-default-evaluation)**

  - When you have pre-synthesized data
  - For evaluating existing privacy-enhanced solutions

6. **Special Scenarios: [Use Cases](./use-cases)**

  - Explore different synthesis application scenarios
  - Handle various practical requirements
  - Provide tested workflow solutions


Simply choose the scenario that matches your needs, prepare the corresponding YAML configuration, and run the code above.