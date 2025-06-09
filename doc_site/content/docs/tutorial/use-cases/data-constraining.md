---
title: Data Constraining
type: docs
weight: 32
prev: docs/tutorial/use-cases/custom-synthesis
next: docs/tutorial/use-cases/ml-utility
---


Constrain synthetic data through field value rules, field combinations, and NA handling strategies.
Current implementation supports three types of constraints: field constraints, field combinations, and NA groups.

Click the below button to run this example in Colab:

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/nics-tw/petsard/blob/main/demo/use-cases/data-constraining.ipynb)

```yaml
---
Loader:
  data:
    filepath: 'benchmark/adult-income.csv'
Preprocessor:
  demo:
    method: 'default'
Synthesizer:
  demo:
    method: 'default'
Postprocessor:
  demo:
    method: 'default'
Constrainer:
  demo:
    nan_groups:
      # Delete entire row when workclass is NA
      workclass: 'delete'
      # Set income to NA if occupation is NA
      occupation:
        'erase':
          - 'income'
      # Copy educational-num value to age when educational-num exists but age is NA
      age:
        'copy':
          'educational-num'
    field_constraints:
      - "age >= 18 & age <= 65" # age limits to 18~65
      - "hours-per-week >= 20 & hours-per-week <= 60" # hours per week limits to 20 ~ 60
    field_combinations:
      -
        - {'education': 'income'}
        - {'Doctorate': ['>50K'], 'Masters': ['>50K', '<=50K']}
Reporter:
  output:
    method: 'save_data'
    source: 'Constrainer'
...
```

## Data Constraint Methods

Data constraint is a refined mechanism for controlling the quality and consistency of synthetic data, allowing users to define acceptable data ranges through multi-layered rules. `PETsARD` provides three primary constraint types: NaN group constraints, field constraints, and field combination constraints. These constraints collectively ensure that generated synthetic data is not only statistically faithful to the original data but also complies with specific domain logic and business regulations.

> Notes:
> 1. All constraint conditions are combined using a strict "all must be satisfied" logic, meaning a single data point must simultaneously satisfy all defined constraint conditions to be retained. In other words, only data records that fully comply with each constraint rule will pass the filter.
> 2. Field combination rules use a positive list approach, affecting only specified values, and do not impact values not mentioned in the fields.
> 3. When using NA values in YAML, always use the string `"pd.NA"`
> 4. Users are strongly recommended to thoroughly examine the original data before defining constraint conditions to ensure that the designed constraint rules accurately reflect the data's inherent characteristics.

### NaN (Missing Value) Group Constraints (`nan_groups`)

- NaN group constraints allow customized handling of missing data
  - `delete`: Delete the entire row when a specific field is NA
  - `erase`: Set other fields to NA when the primary field is NA
  - `copy`: Copy values to other fields when the primary field has a value
- Data constraints do not conflict with data preprocessing missing value handling (`missing`) because the constraint mechanism filters and validates data after synthesis and data restoration. These two steps play complementary roles: the preprocessing stage handles basic missing value issues to assist synthesis, while the constraint mechanism further ensures that synthetic data complies with specific domain logic and statistical specifications.

  ```yaml
  Constrainer:
    demo:
      nan_groups:
        # Delete entire row when workclass is NA
        workclass: 'delete'

        # Set income to NA when occupation is NA
        occupation:
          'erase':
            - 'income'

        # Copy educational-num value to age when age is NA and educational-num has a value
        age:
          'copy':
            'educational-num'
  ```

### Field Constraints (`field_constraints`)

- Field constraints allow setting specific value range rules for individual fields
- Supported operators:
  - Comparison operators: `>`, `>=`, `==`, `!=`, `<`, `<=`
  - Logical operators: `&` (and), `|` (or)
  - Special checks: `IS`, `IS NOT`
  - Date function: `DATE()` function allows declaring specific dates and flexibly combining with other fields and logical operators
- The current field constraint implementation in `PETsARD` uses a custom syntax parser that supports complex logical operations and field comparisons, capable of handling nested boolean expressions. However, some functional limitations exist. For specific constraint needs or complex filtering logic that cannot be satisfied, it is recommended to remove extreme cases from the original data or contact the CAPE team directly for more customized solutions.

  ```yaml
  Constrainer:
    demo:
      field_constraints:
        - "age >= 18 & age <= 65"  # Age limit between 18-65
        - "hours-per-week >= 20 & hours-per-week <= 60"  # Work hours limit between 20-60
        - "income == '<=50K' | (age > 50 & hours-per-week < 40)"  # Low income or older with fewer work hours
        - "native-country IS NOT 'United-States'"  # Non-US nationality
        - "occupation IS pd.NA"  # Missing occupation information
        - "education == 'Doctorate' & income == '>50K'"  # Doctorate must have high income
        - "(race != 'White') == (income == '>50K')"  # Mutually exclusive check between non-white race and high income
        - "(marital-status == 'Married-civ-spouse' & hours-per-week > 40) | (marital-status == 'Never-married' & age < 30)" # Complex logical combination
  ```

### Field Combination Constraints (`field_combinations`)

- Field combination constraints allow defining value range relationships between different fields
- Supported combination types:
  - Single field mapping: Constraints based on a single field's values
  - Multiple field mapping: Simultaneously considering multiple field values for more complex constraints
- For the example below:
  - For income: Only Doctorate and Masters' incomes are constrained, Bachelor's income is not affected
  - For salary: Only Doctorate from the US, Canada, and the UK have specific salary range limits
  - Doctorates from countries other than these three, or people from these countries who are not Doctorates, will not be filtered or affected
- In the current implementation, field combination constraints use a positive list approach, supporting only explicitly listed value combinations. Numeric fields can enumerate valid values but do not yet support logical numeric comparisons using operators like in field constraints.

  ```yaml
  Constrainer:
    demo:
      field_combinations:
        -
          - {'education': 'income'}
          - {
              'Doctorate': ['>50K'],           # Doctorate only allows high income
              'Masters': ['>50K', '<=50K']      # Masters allows high and low income
            }
        -
          - {('education', 'native-country'): 'salary'}
          - {
              ('Doctorate', 'United-States'): [90000, 100000],    # Doctorate in the US, salary range
              ('Doctorate', 'Canada'): [85000, 95000],             # Doctorate in Canada, salary range
              ('Doctorate', 'United-Kingdom'): [80000, 90000]      # Doctorate in the UK, salary range
            }
  ```