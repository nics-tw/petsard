---
title: Anonymeter Privacy risk evaluation
type: docs
weight: 84
prev: docs/developer-guide/benchmark-datasets
next: docs/developer-guide/mpuccs
math: true
---

Anonymeter is a Python library developed by [Statice](https://www.statice.ai/) for evaluating privacy risks in synthetic tabular data. The tool implements the anonymization evaluation standards proposed by the Article 29 Working Party (WP29) of EU Data Protection Directive in 2014 and received endorsement from the French Data Protection Authority (CNIL) in 2023.

## Assessment Framework

Anonymeter evaluates privacy risks from three perspectives:

### Singling Out Risk

Assesses the possibility of identifying specific individuals within the data. For example: "finding an individual with unique characteristics X, Y, and Z."

### Linkability Risk

Evaluates the possibility of linking records belonging to the same individual across different datasets. For example: "determining that records A and B belong to the same person."

For handling mixed data types, this assessment uses Gower's Distance:
- Numerical variables: Normalized absolute difference
- Categorical variables: Distance of 1 if unequal

### Inference Risk

Measures the possibility of inferring attributes from known characteristics. For example: "determining characteristic Z for individuals with characteristics X and Y."

## Risk Calculation

### Privacy Risk Score

Privacy risk is calculated using the following formula:

$$
Privacy Risk = \frac{Attack Rate_{Main} - Attack Rate_{Control}}{1 - Attack Rate_{Control}}
$$

This formula measures:
- Numerator: Additional risk introduced by synthetic data (relative to control group)
- Denominator: Maximum effect of ideal attack (relative to control group)

Scores range from 0-1, with higher values indicating greater privacy risk.

### Attack Success Rate

Attack success rate is calculated using Wilson score:

$$
Attack Rate = \frac{N_{Success} + \frac{Z^2}{2}}{N_{Total} + Z^2}
$$

Where:
- N_Success: Number of successful attacks
- N_Total: Total number of attacks
- Z: Z-score for 95% confidence level

### Three Types of Attack Rates

1. **Main Attack Rate**: Success rate of using synthetic data to infer original data

2. **Baseline Attack Rate**: Success rate of random guessing
   - Main attack rate below baseline indicates invalid assessment results
   - Possible causes: insufficient attack attempts, limited auxiliary information, data issues

3. **Control Attack Rate**: Success rate of using synthetic data to infer control group data

## References

- [WP29 Guidelines](https://ec.europa.eu/justice/article-29/documentation/opinion-recommendation/files/2014/wp216_en.pdf)
- [Anonymeter GitHub](https://github.com/statice/anonymeter)
- [CNIL Opinion](https://www.cnil.fr/en/home)
