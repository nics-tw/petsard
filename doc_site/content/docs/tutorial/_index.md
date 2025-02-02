---
title: Tutorial
type: docs
weight: 11
prev: docs/get-started
sidebar:
  open: true
---


You can run these examples by executing the following code with your YAML config file:

```python
exec = Executor(config=yaml_path)
exec.run()
```

The following scenarios guide you in choosing the right YAML configuration:

1. **Basic Usage**: [Default Synthesis](docs/tutorial/default-synthesis)

  - When you only need basic data synthesis
  - For simple privacy-enhanced synthetic data generation

2. **Basic Usage with Evaluation**: [Default Synthesis and Evaluation](docs/tutorial/default-synthesis-default-evaluation)

  - When you need both synthesis and comprehensive evaluation
  - Includes protection, fidelity, and utility assessments

3. **Evaluation of External Solutions**: [External Synthesis with Default Evaluation](docs/tutorial/external-synthesis-default-evaluation)

  - When you have pre-synthesized data
  - For evaluating existing privacy-enhanced solutions

4. **Special Scenarios**: [Special Cases](docs/tutorial/special-cases)

  - For specific requirements or exceptions
  - Contains solutions for unique data situations


Simply choose the scenario that matches your needs, prepare the corresponding YAML configuration, and run the code above.