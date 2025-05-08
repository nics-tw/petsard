---
title: Multi-Timestamp data - Time Anchoring
type: docs
weight: 42
prev: docs/best-practices/multi-table
next: docs/best-practices/high-cardinality
---

## Case Background

A policy-based financial institution possesses rich enterprise financing-related data, including company basic information, financing applications, financial changes, and other multi-faceted historical records. The institution hopes to promote innovative cooperation with fintech businesses through synthetic data technology, allowing third parties to develop risk prediction models using this data while ensuring data privacy, thereby helping the institution improve risk management efficiency.

### Data Characteristics and Challenges

- **Complex Table Structure**: Original data is distributed across multiple business systems' tables, involving company basic data, application records, financial tracking, and other different aspects
  - Processing method see [Multi-Table data - Denormalization](docs/best-practices/multi-table)
- **Time-Series Data**: Contains multiple key time points (such as application date, approval date, tracking time, etc.), and there are logical sequential relationships between these time points

## Synthesis Challenges for Multi-Timestamp Data

Multi-timestamp data refers to data that records multiple key time nodes with clear temporal relationships within the same business process or entity lifecycle. Unlike time series data, multi-timestamp data does not consist of equidistant observations, but rather represents important milestones in a business process, such as the establishment of a company, financing application, and approval. The core feature of this type of data is that there are clear business logic and dependency relationships between the timestamps.

In the field of synthetic data, multi-timestamp data requires special handling because there are clear business logic constraints between different timestamps. For example, a company's loan application time cannot precede its establishment time, and financial tracking time must be after loan approval time. However, currently available open-source synthesizers have obvious deficiencies when processing such data. When inputting multiple timestamps, these synthesizers typically treat each timestamp as an independent time distribution to learn from. Although they may still capture potential business logic relationships from the data, without explicitly specifying these relationships, it's easy to generate synthetic data that violates business logic, such as application dates earlier than establishment dates.

### Demonstration Data

This simulation data is a wide table consolidated from [Multi-table Data - Denormalization](docs/best-practices/multi-table), with only date-related fields extracted here:

| company_id | established_date | first_apply_apply_date | first_apply_approval_date | latest_apply_apply_date | latest_apply_approval_date | latest_track_last_tracking_date |
|------------|------------------|------------------------|---------------------------|--------------------------|----------------------------|--------------------------------|
| C000001    | 2019-11-03       | 2022-01-21             | 2022-03-19                | 2025-01-05               | 2025-01-30                 | 2027-07-19                     |
| C000002    | 2017-01-02       | 2020-12-12             |                          | 2022-12-02               | 2023-01-05                 | 2024-09-26                     |
| C000003    | 2012-05-29       | 2016-05-08             | 2016-06-29                | 2018-04-28               |                           | 2018-12-16                     |
| C000004    | 2010-09-24       |                        |                          |                          |                           |                                |
| C000005    | 2010-07-24       | 2014-07-03             | 2014-08-11                | 2014-01-04               |                           | 2020-06-26                     |

The table shows six date fields:

- established_date (establishment date)
- first_apply_apply_date (first application date)
- first_apply_approval_date (first approval date)
- latest_apply_apply_date (latest application date)
- latest_apply_approval_date (latest approval date)
- latest_track_tracking_date_last_tracking_date (latest tracking date)

The existence and timing of date fields themselves imply important business logic, as observed from the above examples:

- The time difference between establishment date and first application date, such as C000001's 810-day interval, is influenced not only by individual differences but also by industry and economic cycles
- An application date without an approval date, such as C000002's first application, indicates that the application was not approved (or possibly voluntarily withdrawn), corresponding to a "withdrawn" status
- The time gap between application date and tracking date, such as C000003's 232-day interval, reflects the post-application monitoring mechanism. While we didn't delve into tracking history records in multi-table data, interviews revealed that "regular or irregular financial condition tracking is conducted after application approval." This suggests that irregular tracking might indicate high-risk cases or economic policy fluctuations. If there's interest in tracking irregular events, additional features could be established. This example omits such details
- Complete absence of application and tracking records, as with C000004. Interviews revealed that some cases are processed through policy subsidies rather than through active application processes. Such cases not only warrant discussion about whether to include them in analysis but also confirm that the establishment date is the only stable basic time indicator for enterprises

## Synthesizing Time Differences

Based on practical experience, the CAPE team's recommended best practice is what we call "Time Anchoring": designating the most important time column that will never have null values as an anchor, and converting all other timestamps into durations relative to this anchor point with appropriate time precision. After synthesis, these can be restored to absolute dates/times.

For example, preprocessing would transform the simulation data into the following table for the synthesizer to learn from:

| company_id | established_date | first_apply_apply_date | first_apply_approval_date | latest_apply_apply_date | latest_apply_approval_date | latest_track_last_tracking_date |
|------------|------------------|------------------------|---------------------------|--------------------------|----------------------------|--------------------------------|
| C000001    | 2019-11-03       | 810                    | 867                       | 1889                     | 1914                       | 2815                           |
| C000002    | 2017-01-02       | 1440                   |                           | 2160                     | 2194                       | 2824                           |
| C000003    | 2012-05-29       | 1440                   | 1492                      | 2160                     |                            | 2392                           |
| C000004    | 2010-09-24       |                        |                           |                          |                            |                                |
| C000005    | 2010-07-24       | 1440                   | 1479                      | 1260                     |                            | 3624                           |

In PETsARD, we provide the `TimeAnchor` preprocessing module to achieve this. Click the button below to run the example in Colab:

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/nics-tw/petsard/blob/main/demo/best-practices/multi-timestamp.ipynb)

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
          unit: 'D' # D represents measurement in days
```

By setting the company's establishment date as a time anchor point and referencing subsequent application, approval, and tracking times, we can better model the distribution characteristics of these time differences in synthetic data, thereby generating time patterns that better conform to actual business logic.

When performing this type of time anchoring, special attention should be paid to:

1. Selecting appropriate time reference points: Company establishment dates are typically the most stable and universally present timestamps
2. Handling missing values and anomalies: Some time differences may show negative or extreme values, which need to be evaluated for reasonableness
3. Maintaining business logic consistency: Ensuring the correct sequence of events (e.g., applications must precede approvals)
4. Choosing time units: Selecting appropriate time units (days/seconds) based on business requirements

This method offers multiple advantages:

1. Reducing computational load for synthesizers: Converting absolute times to relative time differences simplifies learning
2. Improving type compatibility: Compared to date types, synthesizers usually have better grasp of distributions for integer types (time differences)
3. Strengthening logical constraint learning: Synthesizers learn simple constraints like whether values are greater than zero more effectively
4. Enhancing temporal relationship consistency: More effectively ensures logical coherence between multiple timestamps

## Summary

Time anchoring is a key strategy for synthesizing multi-timestamp data. By setting a company's establishment date as a time anchor point and calculating relative differences for subsequent application, approval, and tracking times, we can better model the distribution characteristics of these time differences in synthetic data. While this transformation primarily helps synthesizers learn, it's still recommended to pair it with specific business constraint checks to ensure the completeness and reasonableness of temporal logic in synthetic data.