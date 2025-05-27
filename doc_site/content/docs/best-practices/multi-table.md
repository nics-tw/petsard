---
title: Multi-Table data - Denormalization
type: docs
weight: 41
prev: docs/best-practices
next: docs/best-practices/multi-timestamp
---

## Case Background

A policy-based financial institution possesses rich enterprise financing-related data, including company basic information, financing applications, financial changes, and other multi-faceted historical records. The institution hopes to promote innovative cooperation with fintech businesses through synthetic data technology, allowing third parties to develop risk prediction models using this data while ensuring data privacy, thereby helping the institution improve risk management efficiency.

### Data Characteristics and Challenges

- **Complex Table Structure**: Original data is distributed across multiple business systems' tables, involving company basic data, application records, financial tracking, and other different aspects
- **Time-Series Data**: Contains multiple key time points (such as application date, approval date, tracking time, etc.), and there are logical sequential relationships between these time points
  - Processing method see [Multi-timestamp Data - Time Anchoring](docs/best-practices/multi-timestamp)

## Data Table Relationships and Business Context

The data structure in this case reflects the complete business process of enterprise financing, primarily consisting of three core data tables:

- Company Basic Information Table:

  - Contains static information such as company identifier, industry category, sub-industry, geographic location, and capital
  - Each record represents an independent business entity
  - This table serves as the primary table, forming one-to-many relationships with other tables

- Financing Application Records Table:

  - Records details of each financing application submitted by companies to the financial institution
  - Includes application type, application date, approval date, application status, and amount information
  - A single company may have multiple financing applications spanning several years
  - The time difference between application date and approval date reflects the processing time
  - Application results are categorized as approved, rejected, or withdrawn

- Financial Tracking Records Table:

  - Records financial performance tracking data after companies receive financing
  - Includes profit ratio indicators, tracking time range, revenue indicators, and risk level assessments
  - Each financing application may generate multiple tracking records, representing financial conditions at different points in time
  - Risk level assessments reflect trends in a company's repayment capacity

These three data tables form a hierarchical relationship structure: Company Basic Information (1) → Financing Application Records (N) → Financial Tracking Records (N). In the actual business process, companies first establish their basic profile, then submit financing applications, with each application case triggering financial tracking mechanisms. It is particularly noteworthy that financial assessments occur not only during the initial application phase but also through regular or irregular financial status tracking during the interim phase after approval, thereby forming a complete and continuously updated data chain. This multi-level, multi-timepoint, one-to-many relationship structure significantly increases the complexity of data synthesis, especially when it is necessary to simultaneously preserve both the relational integrity and time series characteristics of the data.

### Demonstration Data

Considering data privacy, the following uses simulated data to demonstrate data structure and business logic. While these data are simulated, they retain the key characteristics and business constraints of the original data:

#### Company Basic Information

| company_id | industry | sub_industry | city | district | established_date | capital |
|------------|----------|--------------|------|----------|------------------|---------|
| C000001 | 營建工程 | 環保工程 | 新北市 | 板橋區 | 2019-11-03 | 19899000 |
| C000002 | 營建工程 | 建築工程 | 臺北市 | 內湖區 | 2017-01-02 | 17359000 |
| C000003 | 製造業 | 金屬加工 | 臺北市 | 內湖區 | 2012-05-29 | 5452000 |
| C000004 | 營建工程 | 環保工程 | 桃園市 | 中壢區 | 2010-09-24 | 20497000 |
| C000005 | 批發零售 | 零售 | 臺北市 | 內湖區 | 2010-07-24 | 17379000 |

#### Financing Application Records

| application_id | company_id | loan_type | apply_date | approval_date | status | amount_requested | amount_approved |
|----------------|------------|-----------|------------|---------------|--------|------------------|-----------------|
| A00000001 | C000001 | 廠房擴充 | 2022-01-21 | 2022-03-19 | approved | 12848000 | 12432000.0 |
| A00000002 | C000001 | 營運週轉金 | 2025-01-05 | 2025-02-11 | approved | 2076000 | 1516000.0 |
| A00000003 | C000001 | 創新研發 | 2025-01-05 | 2025-01-30 | approved | 11683000 | 10703000.0 |
| A00000004 | C000002 | 營運週轉金 | 2020-12-12 | NaN | rejected | 5533000 | NaN |
| A00000005 | C000002 | 廠房擴充 | 2026-02-14 | NaN | rejected | 1433000 | NaN |

#### Financial Tracking Records

| application_id | profit_ratio_avg_profit_ratio | profit_ratio_min_profit_ratio | profit_ratio_profit_ratio_std | profit_ratio_negative_profit_count | tracking_date_tracking_months | tracking_date_last_tracking_date | revenue_avg_revenue | revenue_revenue_growth | risk_level_last_risk | risk_level_second_last_risk |
|----------------|-----------------------------|-------------------------------|------------------------------|-----------------------------------|-------------------------------|--------------------------------|---------------------|------------------------|----------------------|----------------------------|
| A00000001 | 0.033225 | -0.096496 | 0.084001 | 4 | 3.0 | 2024-09-04 | 1.840486e+07 | -0.026405 | high_risk | normal |
| A00000002 | -0.002636 | -0.080580 | 0.074297 | 6 | 3.0 | 2027-07-31 | 1.926350e+07 | 1.284445 | normal | warning |
| A00000003 | 0.009984 | -0.087006 | 0.084297 | 6 | 3.0 | 2027-07-19 | 2.470124e+07 | 1.561825 | attention | severe |
| A00000007 | 0.002074 | -0.091077 | 0.093598 | 4 | 21.0 | 2024-09-26 | 2.388020e+07 | 0.090593 | attention | normal |
| A00000008 | 0.038045 | -0.033057 | 0.053279 | 3 | 3.0 | 2018-12-16 | 2.390215e+07 | -0.516376 | high_risk | normal |

## Comparison of Multi-table Data Synthesis Methods

Before designing a data synthesis solution, we conducted in-depth research and evaluation of existing multi-table synthesis technologies. Based on the SDV ecosystem (as of February 2025)[^1], the currently publicly available multi-table synthesizers mainly include:

1. Independent Synthesis: Independently builds Copulas for each table, unable to learn inter-table patterns
2. HMA (Hierarchical Modeling Algorithm): Hierarchical machine learning method using 3. recursive techniques to model parent-child relationships in multi-table datasets
3. HSA: Using a segmented algorithm to provide efficient synthesis for large multi-tables, supporting various single-table synthesis methods
4. Day Z: Level 5 calibrated simulation2 from scratch [^2], can synthesize using only metadata

Below is a comparison of these methods (partial):

| **Feature**                    | Day Z | Independent | HMA | HSA |
|--------------------------------|--|--|--|--|
| Synthesis using only metadata  | ✔️ | | | |
| Apply constraints              | | ✔️ | ✔️ | ✔️ |
| Maintain referential integrity | ✔️ | ✔️ | ✔️ | ✔️ |
| Learn intra-table patterns     | | ✔️ | ✔️ | ✔️ |
| Learn inter-table patterns     | | ✔️ | ✔️ |
| Scalability                    | ✔️ | ✔️ | | ✔️ |
| Availability                   | Enterprise only | Enterprise only | Open | Enterprise only |

After evaluation, we found that although HMA is the best and only available open-source option, it still has obvious limitations:

1. **Scale and complexity limitations**: HMA is most suitable for structures with no more than 5 tables and only 1 layer of parent-child relationships
2. **Numerical field limitations**: HMA can only be used for synthesizing numerical fields, categorical fields must all be pre-processed and transformed
3. **Modeling limitations**: HMA is only applicable to parametric distributions with predefined parameter quantities; non-parametric estimation for multi-peak distributions is only available in the paid version
4. **Constraint limitations**: Certain important constraint conditions are only available in the paid version
5. **Fields limitations**: In the official simplified model function `simplify_schema()`, total fields are limited to less than 1,000
6. **Records limitations**: Official documentation states that HMA is not suitable for large amounts of data, though no specific limit is declared

There are also limitations for all SDV multi-table synthesizers:

7. **Single foreign key limitation**: Metadata can only declare a single field in the parent table corresponding to a single field in the child table, and cannot support multiple field combinations or even combined conditions
8. **One-to-many relationship limitation**: The relationship between parent and child tables must be one-to-many, not supporting many-to-many, or even one-to-one.

All of the above limitations are listed in SDV's documentation. But our team went further, testing with SDV's official `fake_hotel`s` small test dataset, with a parent hotel table containing 5 fields and 10 records, and a child guest table with 10 fields and 658 records. In actual testing, we found that HMA could indeed complete processing in about 2 seconds, but there were significant issues with model quality:

- Low cross-table correlations (e.g., amenities fee correlation only 0.14)
- Insufficient association between categorical variables (e.g., similarity between city and rating only 0.20)
- Some data items could not be correctly associated (e.g., amenities fee and check-in date)

Upon observation, the main cause was that the original data had many bimodal distributions, with a large portion of people not giving tips (amenities_fee = 0). These parametric statistical limitations, coupled with the constraint limitations after categorical field encoding, made us understand that HMA is not suitable for use as a product or service.

## The Necessity of Database Denormalization

Based on the above research, we believe that current open-source multi-table synthesis technology is not yet mature enough to directly handle complex enterprise financing data. Open-source algorithm versions mostly only support fewer data field numbers and fewer data records, and there is no clear guidance on the correspondence between data tables. For complex multi-table data, we need to apply traditional database techniques systematically and structurally in the synthetic data process.

After CAPE team evaluation, we recommend:

1. **Pre-integration into a data warehouse****: Define appropriate granularity according to downstream task purposes. For example, if we are concerned with the increase or decrease in each company's latest financial status, the appropriate granularity would be one record per company
2. **Plan suitable integration methods using professional knowledge**: When tables of different granularity need to be integrated, data owners need to plan the most suitable integration method based on domain knowledge

In this demonstration, we integrate company basic information, financing application records, and financial tracking into a wide table with "application case" as the unit. Company basic data (such as industry category, capital) is directly included, while financing applications take the first and latest application records, and financial tracking takes the latest tracking. This preserves necessary time series information while avoiding overly complex table structures.

Here we demonstrate using `pandas.merge`, but integration methods are not limited to Python. Considering data volume, we recommend pre-processing within database systems using SQL or similar methods. For multi-table data, we only recommend preparing one table outside of PETsARD, as PETsARD has no plans to support denormalization functionality.

```python
# Mark each company's first and latest application
applications['sort_tuple'] = list(zip(applications['apply_date'], applications['application_id']))

# Find the earliest application for each company
min_tuples = applications.groupby('company_id')['sort_tuple'].transform('min')
applications['is_first_application'] = (applications['sort_tuple'] == min_tuples)

# Find the latest application for each company
max_tuples = applications.groupby('company_id')['sort_tuple'].transform('max')
applications['is_latest_application'] = (applications['sort_tuple'] == max_tuples)

applications.drop(columns=['sort_tuple'], inplace=True, errors='ignore')


# Join financial tracking data with application data to get company IDs
tracking_w_company = tracking\
    .merge(
        applications[['company_id', 'application_id']],
        how='left',
        left_on='application_id',
        right_on='application_id'
    )

# Mark the latest financial tracking record for each company
tracking_w_company['sort_tuple'] = list(zip(tracking_w_company['tracking_date_last_tracking_date'], tracking_w_company['application_id']))

max_tuples = tracking_w_company.groupby('company_id')['sort_tuple'].transform('max')
tracking_w_company['is_latest_tracking'] = (tracking_w_company['sort_tuple'] == max_tuples)

tracking_w_company.drop(columns=['sort_tuple'], inplace=True, errors='ignore')


# Merge company data and application data
denorm_data: pd.DataFrame = companies\
    .merge(
        applications[applications['is_first_application']].add_prefix('first_apply_'),
        how='left',
        left_on='company_id',
        right_on='first_apply_company_id'
    ).drop(columns=['first_apply_company_id', 'first_apply_is_first_application'])\
    .merge(
        applications[applications['is_latest_application']].add_prefix('latest_apply_'),
        how='left',
        left_on='company_id',
        right_on='latest_apply_company_id'
    ).drop(columns=['latest_apply_company_id', 'first_apply_is_latest_application'])

# Add summarized tracking data
denorm_data = denorm_data\
   .merge(
       tracking[tracking['is_latest_tracking']].add_prefix('latest_track_'),
       how='left',
       left_on='company_id',
       right_on='latest_track_company_id'
   ).drop(columns=['latest_track_company_id', 'latest_track_is_latest_tracking'])
```

Click the button below to run the example in Colab:

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/nics-tw/petsard/blob/main/demo/best-practices/multi-table.ipynb)

PETsARD runs simply with the most default settings

```yaml
---
Loader:
  data:
    filepath: 'best-practices_multi-table.csv'
Preprocessor:
  demo:
    method: 'default'
Synthesizer:
  demo:
    method: 'default'
Postprocessor:
  demo:
    method: 'default'
Reporter:
  output:
    method: 'save_data'
    source: 'Postprocessor'
...
```

When performing this type of data integration, special attention should be paid to:

1. **Confirm primary key relationships**: Avoiding duplication or omission
2. **Properly handle time series information**: For example, using summary statistics to preserve important features
3. **Table merging order**: This will affect the final result; it is recommended to process tables with stronger relationships first
4. **Downstream task requirements**: To reduce synthesis complexity, only necessary fields can be retained

Through preliminary denormalization processing, we can:

- Clearly preserve business logic relationships
- Reduce data distortion during the synthesis process
- Improve the utility and quality of the final synthetic data

## Summary

In this part, we explored the current research status and limitations of multi-table data synthesis, and explained why traditional database denormalization processing is crucial for complex financial data. Pre-integration of data can not only overcome the limitations of existing synthesis technologies but also more effectively preserve business logic and time series characteristics.

The next section will delve into how to handle multi-time point data generated after integration.

## References

[^1]: https://docs.sdv.dev/sdv/multi-table-data/modeling/synthesizers
[^2]: Balch, T., Potluru, V. K., Paramanand, D., & Veloso, M. (2024). Six Levels of Privacy: A Framework for Financial Synthetic Data. arXiv preprint. arXiv:2403.14724 [cs.CR]. https://doi.org/10.48550/arXiv.2403.14724
