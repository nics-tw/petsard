---
title: Use Cases
type: docs
weight: 15
prev: docs/tutorial/external-synthesis-default-evaluation
next: docs/tutorial
sidebar:
  open: true
---


When developing privacy-preserving data synthesis workflows, you may encounter special requirements. The following scenarios will help you handle these situations. Each topics provides complete examples that you can execute and test directly through Colab links.

## **Data Understanding**:

### **Data Insights: [Data Description](./data-description)**

  - Understand your data before synthesis
  - Analyze data characteristics at different granularities
  - Includes global, column-wise, and pairwise statistics

## **Data Generating**:

- If the synthesis results are not satisfactory, you can:
  - Try different synthesis algorithms
  - Adjust model parameters (if any)
  - Perform more detailed data preprocessing

### **Data Quality Enhancement: [Data Preprocessing](./data-preprocessing)**

  - Systematically address various data quality issues
  - Provide multiple methods for handling missing values, encoding, and outliers
  - Include uniform encoding, standardization, and discretization techniques

### **Synthesis Method Selection: [Comparing Synthesizers](./comparing-synthesizers)**

  - Compare effects of different synthesis algorithms
  - Use multiple algorithms in a single experiment
  - Includes Gaussian Copula, CTGAN, and TVAE

### **Custom Synthesis: [Custom Synthesis](./custom-synthesis)**

  - Create your own synthesis methods
  - Integrate into PETsARD's synthesis workflow

### **Data Plausibility: [Data Constraining](./data-constraining)**

  - Ensure synthetic data complies with real business rules
  - Provide constraints for field values, field combinations, and null values
  - Include numeric range limits, category relationships, and null handling strategies

## **Data Evaluating**

### **Machine Learning-based Data Utility：[ML Utility](./ml-utility)**

  - Evaluate synthetic data utility for classification, regression, and clustering
  - Uses dual-source control group evaluation by default for fair comparison
  - Support multiple experimental designs for different use cases

### **Custom Evaluation: [Custom Evaluation](./custom-evaluation)**

  - Create your own evaluation methods
  - Implement assessments at different granularities
  - Integrate into PETsARD's evaluation workflow

## **Workflow improvement**

### **Workflow Validation: [Benchmark Datasets](./benchmark-datasets)**

  - Test your synthesis workflow on benchmark data
  - Verify synthesis parameter settings
  - Provide reliable reference standards

### **Performance Analysis: [Timing](./timing)**

  - Monitor execution time for each module in your pipeline
  - Identify performance bottlenecks in your workflow
  - Compare execution times across different configurations
  - Generate timing reports for performance analysis