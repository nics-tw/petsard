---
title: Best practices
type: docs
weight: 40
prev: docs/tutorial
next: docs/api
sidebar:
  open: false
---


## **Choosing Synthesis Scenarios**

Most existing tabular data synthesis algorithms focus on algorithmic development, with few offering complete business solutions. When facing the complexity and incompleteness of real-world data, customization by consulting teams is often required for different application domains.

In light of this, since 2024, the CAPE team has been assisting Taiwan's public enterprises and financial institutions in implementing synthetic data applications, developing a methodology from practical experience. We share our practical insights and demonstrate how to utilize `PETsARD` to address the most common and critical real data patterns, aiming to provide valuable references for data science and privacy protection teams both domestically and internationally.

## Best Practices

### **[Multi-table](./multi-table) and [Multi-timestamp](./multi-timestamp) Data Synthesis: A Corporate Data Case Study**

- Collaborated with a policy-based financial institution to synthesize corporate customer data (including basic information, financing applications, and financial tracking), enabling them to host datathon competitions that invite external vendors to tackle business challenges.
- The dataset spans multiple business tables with complex relationships, containing multiple key timestamps from company establishment through financing applications to financial tracking, exhibiting clear temporal characteristics and business logic relationships
- The case study demonstrates how to effectively handle multi-table and multi-timestamp data through [denormalization](./multi-table) and [time anchoring](./multi-timestamp) methods, ensuring synthetic data preserves the business logic and temporal relationships of the original data
- This best practice is applicable to processing data in similar scenarios such as corporate financing, loan applications and tracking, especially when dealing with business data that has complex table structures and involves multiple time nodes

### **Synthesizing Low-Cardinality Data: Social Services Data Case Study (WIP)**

- Collaborating with a municipal social protection service agency to synthesize cross-institutional (social affairs, police, medical) assessment and intervention questionnaires, covering initial evaluations and follow-up visits
- The dataset primarily consists of yes/no questions, single-choice, and multiple-choice questions, characterized by few options and uneven response distributions
- This best practice applies to similar low-cardinality data scenarios, such as market research surveys, user experience studies, public opinion polls, and socioeconomic statistics, particularly when dealing with structured questionnaires with standardized options

### **[Synthesizing High-Cardinality and Multi-Table Data](./high-cardinality-multi-table): Enterprise Data Case Study**

- Collaborating with a policy-oriented financial institution to synthesize enterprise client data (including basic information, financing applications, and financial tracking)
- The dataset spans multiple business tables with complex relationships, and due to diverse industry categories and numerous financing programs, exhibits high cardinality (numerous unique values) in many fields, along with longitudinal tracking characteristics
- This best practice applies to similar high-cardinality and multi-table data scenarios, such as enterprise credit databases, industry research data, and longitudinal records, particularly when handling business data with complex table structures

### **Synthesizing Imbalanced Data: Insurance Data Case Study (WIP)**

- Collaborating with a Taiwanese financial holding group to synthesize insurance policy, claims, and medical visit data from its life insurance subsidiary, supporting cross-enterprise fraud detection model development
- The dataset's key target variable is claims review results, with rejected claims accounting for only 3%, representing a typical class imbalance case
- This best practice applies to similar imbalanced data scenarios, such as credit card fraud detection, cybersecurity threat identification, and anomalous transaction screening, particularly when handling highly skewed target distributions