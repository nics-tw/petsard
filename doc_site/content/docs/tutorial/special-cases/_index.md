---
title: Special cases
type: docs
weight: 15
prev: docs/tutorial/external-synthesis-default-evaluation
next: docs/tutorial/special-cases/data-description
sidebar:
  open: true
---


When developing privacy-preserving data synthesis workflows, you may encounter special requirements. The following scenarios will help you handle these situations:

1. **Data Understanding**: [Data Description](docs/tutorial/special-cases/data-description)
   - Understand your data before synthesis
   - Analyze data characteristics at different granularities
   - Includes global, column-wise, and pairwise statistics

2. **Synthesis Method Selection**: [Comparing Synthesizers](docs/tutorial/special-cases/comparing-synthesizers)
   - Compare effects of different synthesis algorithms
   - Use multiple algorithms in a single experiment
   - Includes Gaussian Copula, CTGAN, and TVAE

3. **Data Quality Enhancement**: [Handling Missing Values](docs/tutorial/special-cases/handling-missing-values)
   - Handle missing values in data
   - Use different methods for different columns
   - Includes dropping, statistical imputation, and custom imputation

4. **Workflow Validation**: [Benchmark Datasets](docs/tutorial/special-cases/benchmark-datasets)
   - Test your synthesis workflow on benchmark data
   - Verify synthesis parameter settings
   - Provide reliable reference standards

5. **Custom Evaluation**: [Custom Evaluation](docs/tutorial/special-cases/custom-evaluation)
   - Create your own evaluation methods
   - Implement assessments at different granularities
   - Integrate into PETsARD's evaluation workflow

Each special case provides complete examples that you can execute and test directly through Colab links.