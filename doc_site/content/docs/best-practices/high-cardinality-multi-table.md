---
title: Synthesizing High-Cardinality and Multi-Table Data
type: docs
weight: 41
prev: docs/best-practices
next: docs/best-practices
---

## Background

A policy-oriented financial institution possesses rich enterprise financing data, including company basic information, financing applications, and financial tracking records across multiple dimensions. The institution aims to promote innovative collaboration with fintech companies through synthetic data technology, enabling third parties to develop risk prediction models while ensuring data privacy, thereby enhancing the institution's risk management capabilities.

## Data Characteristics and Challenges

- **Complex Table Structure**: Original data is distributed across multiple business system tables, involving company basic information, application records, and financial tracking
- **High-Cardinality Categorical Variables**: Due to diverse industry categories and numerous financing programs, many fields contain a large number of unique values
- **Time-Series Data**: Contains multiple key time points (such as application date, approval date, tracking dates), with logical sequential relationships
- **Data Quality Issues**: Includes missing values, anomalies, and complexity in cross-table integration

## Simulated Data Demonstration

Considering data privacy, the following uses simulated data to demonstrate data structure and business logic. While these data are simulated, they retain the key characteristics and business constraints of the original data:

### Company Basic Information


```python
# Example of company basic information
company_info = pd.DataFrame({
   'company_id': ['C000001', 'C000002', 'C000003'],
   'industry': ['Manufacturing', 'Service', 'Wholesale and Retail'],
   'sub_industry': ['Electronic Components', 'Logistics', 'E-commerce'],
   'city': ['New Taipei City', 'Taipei City', 'Taoyuan City'],
   'district': ['Banqiao District', 'Neihu District', 'Zhongli District'],
   'established_date': ['2015-03-15', '2018-06-20', '2016-09-10'],
   'capital': [15000000, 8000000, 12000000]  # Unit: NTD
})
```

### Financing Application Records

```python
# Example of financing applications
applications = pd.DataFrame({
    'application_id': ['A00000001', 'A00000002', 'A00000003', 'A00000004'],
    'company_id': ['C000001', 'C000001', 'C000002', 'C000003'],
    'loan_type': ['Operating Capital', 'Equipment Purchase', 'Operating Capital', 'Digital Transformation'],
    'apply_date': ['2023-03-15', '2023-09-20', '2023-05-10', '2023-07-01'],
    'approval_date': ['2023-04-10', '2023-10-15', None, '2023-07-25'],
    'status': ['approved', 'approved', 'rejected', 'approved'],
    'amount_requested': [5000000, 8000000, 3000000, 4000000],  # Unit: NTD
    'amount_approved': [4000000, 7000000, None, 3500000]       # Unit: NTD
})
```

### Financial Tracking Records

```python
# Example of financial tracking
tracking = pd.DataFrame({
    'track_id': ['T00000001', 'T00000002', 'T00000003', 'T00000004'],
    'application_id': ['A00000001', 'A00000001', 'A00000004', 'A00000004'],
    'company_id': ['C000001', 'C000001', 'C000003', 'C000003'],
    'tracking_date': ['2023-07-10', '2023-10-10', '2023-10-25', '2024-01-25'],
    'revenue': [12000000, 13500000, 8000000, 7500000],   # Unit: NTD
    'profit': [600000, 810000, 240000, -150000],         # Unit: NTD
    'profit_ratio': [0.05, 0.06, 0.03, -0.02],           # Unit: %
    'risk_level': ['normal', 'normal', 'attention', 'high_risk']
})
```

### Business Logic Constraints

1. Temporal Constraints:
  - Application date must be after company establishment date
  - Approval date must be within 1-60 days after the application date
  - Financial tracking date must be after the approval date, with quarterly (90-day) intervals

2. Amount Constraints:
  - Company capital must be over 1 million
  - Approved amount is typically 60-100% of the requested amount
  - Single application amount must not exceed 200% of capital

3. Risk Assessment Rules:
  - Risk level is determined by profit ratio intervals:
    - Profit ratio > 5%: Normal
    - Profit ratio 0-5%: Attention/Warning
    - Profit ratio < 0%: High Risk
  - Note: Profit ratio is simplified as profit divided by revenue. Actual financial risk assessment models may use more complex evaluation mechanisms.

## `PETsARD` Solution

1. **Data Integration and Quality Enhancement**
   - Utilize database denormalization techniques to integrate multiple tables into a single wide table
   - Use `PETsARD`'s data quality detection features to ensure data consistency during integration
   - Provide systematic methods for handling missing and anomalous values

2. **High-Cardinality Category Processing**
   - Perform distribution analysis on high-cardinality fields to identify key categories
   - Design and implement constraint conditions to ensure synthetic data meets business logic
   - Avoid generating category combinations that are practically impossible

3. **Time-Series Data Processing**
   - Employ time anchor (`TimeAnchor`) technology to handle multiple time points
   - Maintain logical order relationships between time points
   - Reasonably handle missing values in time series

### Database Denormalization Processing

Currently, existing synthetic data technologies for multiple tables mostly support a limited number of data columns and rows, with unclear guidelines for table relationships. After evaluation by the CAPE team, it is recommended to:
- Determine an appropriate granularity based on downstream task objectives (in this case, loan application risk deterioration)
- Pre-integrate into a data warehouse
- Allow data owners to plan appropriate integrated columns

In this demonstration, we integrate three tables (company basic information, financing application records, and financial tracking) into a wide table with "application case" as the unit. Enterprise basic information (such as industry category, capital) is directly imported, and financial tracking calculates summary statistics (such as average risk level over three years, most recent risk level), preserving necessary time series information while avoiding overly complex table structures.

When performing such data integration, special attention is needed:
1. Confirm primary key relationships to avoid duplication or omission
2. Properly handle time series information, such as using summary statistics to retain important features
3. The order of table merging affects the final result; it is recommended to first process tables with stronger associations
4. Consider downstream task requirements and retain only necessary columns to reduce synthesis complexity

### Handling High-Cardinality Categories

Since synthetic data is based on probabilistic models, while capable of learning implicit relational structures, extreme scenarios that violate business logic may arise during large-scale sampling. Constraint conditions are designed to ensure synthetic data complies with business regulations.

For example, while our demonstration lists only four main industries with five sub-industries each, the Directorate-General of Budget, Accounting and Statistics actually classifies Taiwanese industries into 19 major categories, 88 medium categories, 249 small categories, and 527 fine categories. More importantly, different industries exhibit varying financing needs and default risks due to economic cycles, making it crucial to maintain the business logic of industry classifications.

```yaml
Constrainer:
  demo:
    field_combinations:
      -
        - {'industry': 'sub_industry'}   # Industry category relationships
        - {
            'Manufacturing': ['Electronic Components', 'Metal Processing', 'Textile', 'Food', 'Plastic Products'],
            'Service': ['Catering', 'Logistics', 'Education', 'Leisure Entertainment', 'Professional Consulting'],
            'Wholesale and Retail': ['E-commerce', 'Import and Export Trade', 'Retail', 'Automotive Parts', 'Consumer Goods'],
            'Construction Engineering': ['Civil Engineering', 'Construction', 'Interior Decoration', 'Mechanical and Electrical Engineering', 'Environmental Engineering']
            }
```

The same principle can be applied to non-high-cardinality fields. For any field with clear business logic, it is recommended to add constraint conditions. Through repeated constraint, filtering, and resampling processes, we can maintain data fidelity while ensuring the reasonableness of synthetic data.

Here are more constraint examples:

```yaml
Constrainer:
 demo:
   nan_groups:
     company_id: delete
     # If company ID is missing, delete entire record

     industry:
       erase: 'sub_industry'
     # If main industry is missing, erase sub-industry

     approval_date:
       erase: ['risk_level_last_risk', 'risk_level_second_last_risk']
     # If approval date is missing, clear risk rating related fields

   field_constraints:
     - "established_date <= apply_date"
     # Establishment date must not be later than application date

     - "apply_date <= approval_date"
     # Application date must not be later than approval date

     - "capital >= 1000000"
     # Capital must be at least 1 million

     - "amount_requested <= capital + capital"
     # Requested amount cannot exceed 2 times of capital

     - "amount_approved <= amount_requested"
     # Approved amount cannot exceed requested amount

     - "profit_ratio_min_profit_ratio <= profit_ratio_avg_profit_ratio"
     # Profit ratio must be within reasonable range

   field_combinations:
     -
       - {'industry': 'sub_industry'}
       # Industry category relationships
       - {
           'Manufacturing': ['Electronic Components', 'Metal Processing', 'Textile', 'Food', 'Plastic Products'],
           'Service': ['Catering', 'Logistics', 'Education', 'Leisure Entertainment', 'Professional Consulting'],
           'Wholesale and Retail': ['E-commerce', 'Import and Export Trade', 'Retail', 'Automotive Parts', 'Consumer Goods'],
           'Construction Engineering': ['Civil Engineering', 'Construction', 'Interior Decoration', 'Mechanical and Electrical Engineering', 'Environmental Engineering']
         }
```

The CAPE team recommends that data owners thoroughly use domain knowledge to organize data before synthesis. For example, for industries that have been abolished or have extremely low usage frequency, it is recommended to merge or reclassify them during the database organization stage. The more concise and clean the data quality, the better the final synthesis results.

### Simulating Time Differences

When a dataset contains multiple time fields, there are often potential business logic relationships between them. For instance, in enterprise financing scenarios, the time difference from establishment to first financing application may vary significantly across industries: manufacturing might require a longer preparation period, while service industries might need operational capital more quickly. Similarly, processing time from application to approval may differ due to industry characteristics and economic cycles.

While temporal sequence (such as establishment date being earlier than application date) can be maintained through constraint conditions, these subtle time difference patterns are suitable for handling with `TimeAnchor`:

```yaml
Preprocessor:
  demo:
    method: 'default'
    config:
      scaler:
        'established_date':
          # Using company establishment date as anchor to calculate day differences
          # with application, approval and tracking dates
          method: 'scaler_timeanchor'
          reference:
            - 'apply_date'
            - 'approval_date'
            - 'tracking_date_last_tracking_date'
          unit: 'D'
```

By setting the company establishment date as the time anchor and referencing subsequent application, approval, and tracking times, we can better simulate the distribution characteristics of these time differences, thereby generating time series patterns that better match actual business logic.

### Conclusion and Recommendations

Through this case, we demonstrate the core concepts of handling high-cardinality and multi-table data:

1. **Data Integration Strategy**:
   - Choose appropriate data granularity based on downstream tasks
   - Simplify table structure through data denormalization
   - Preserve time series features using summary statistics

2. **Maintaining Data Reasonableness**:
   - Design constraints for high-cardinality categories
   - Maintain business logic relationships between fields
   - Simulate time difference distribution characteristics

3. **Data Quality Recommendations**:
   - Encourage data owners to use domain knowledge in preprocessing
   - Merge or reclassify low-usage categories
   - Clearly define business meanings of data fields

These methods are not only applicable to financial data but also valuable for other datasets with complex category structures and temporal characteristics, such as medical records and industry research.

## Full Demonstration

Click the button below to run the example in Colab:

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/nics-tw/petsard/blob/main/demo/best-practices-high-cardinality-multi-table.ipynb)

```yaml
---
Loader:
  data:
    filepath: 'best-practices-high-cardinality-multi-table.csv'
Preprocessor:
  demo:
    method: 'default'
    config:
      scaler:
        'established_date':
          # Using company establishment date as anchor to calculate day differences
          # with application, approval and tracking dates
          method: 'scaler_timeanchor'
          reference:
            - 'apply_date'
            - 'approval_date'
            - 'tracking_date_last_tracking_date'
          unit: 'D'
Synthesizer:
  demo:
    method: 'default'
Postprocessor:
  demo:
    method: 'default'
Constrainer:
  demo:
    nan_groups:
      company_id: delete
      # If company ID is missing, delete entire record

      industry:
        erase: 'sub_industry'
      # If main industry is missing, erase sub-industry

      approval_date:
        erase: ['risk_level_last_risk', 'risk_level_second_last_risk']
      # If approval date is missing, clear risk rating related fields

    field_constraints:
      - "established_date <= apply_date"
      # Establishment date must not be later than application date
      - "apply_date <= approval_date"
      # Application date must not be later than approval date

      - "capital >= 1000000"
      # Capital must be at least 1 million

      - "amount_requested <= capital + capital"
      # Requested amount cannot exceed 2 times of capital

      - "amount_approved <= amount_requested"
      # Approved amount cannot exceed requested amount

      - "profit_ratio_min_profit_ratio <= profit_ratio_avg_profit_ratio"
      # Profit ratio must be within reasonable range

    field_combinations:
      -
        - {'industry': 'sub_industry'}
        # Industry category relationships
        - {
            'Manufacturing': ['Electronic Components', 'Metal Processing', 'Textile', 'Food', 'Plastic Products'],
            'Service': ['Catering', 'Logistics', 'Education', 'Leisure Entertainment', 'Professional Consulting'],
            'Wholesale and Retail': ['E-commerce', 'Import and Export Trade', 'Retail', 'Automotive Parts', 'Consumer Goods'],
            'Construction Engineering': ['Civil Engineering', 'Construction', 'Interior Decoration', 'Mechanical and Electrical Engineering', 'Environmental Engineering']
          }
Reporter:
  output:
    method: 'save_data'
    source: 'Constrainer'
...
```