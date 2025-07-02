---
title: Constrainer
type: docs
weight: 57
prev: docs/api/synthesizer
next: docs/api/evaluator
---


```python
Constrainer(config)
```

Data constraint handler for synthetic data generation. Supports NaN handling, field-level constraints, and field combination rules.

## Parameters

- `config` (dict): Constraint configuration dictionary containing the following keys:

  - `nan_groups` (dict): NaN handling rules
    - Key: Column name with NaN values
    - Value for 'delete' action: String 'delete'
    - Value for 'erase' and 'copy' actions: Dictionary containing action and target fields
      - For 'erase': `{'erase': target_field}` where target_field can be a string or list of strings
      - For 'copy': `{'copy': target_field}` where target_field is a string
    - Value for 'nan_if_condition' action: `{'nan_if_condition': condition_dict}`
      - condition_dict is a dictionary where:
        - Key: Target field name to check condition
        - Value: Matching value(s) in the target field (can be a single value or list of values)
      - When values in target fields match the specified conditions, the main field will be set to pd.NA

  - `field_constraints` (List[str]): Field-level constraints as string expressions
    - Support operators: >, >=, ==, !=, <, <=, IS, IS NOT
    - Support logical operators: &, |
    - Support bracketed expressions
    - Special value: "pd.NA" for NULL checks
    - DATE() function for date comparisons

  - `field_combinations` (List[tuple]): Field combination rules
    - Each tuple contains (field_map, allowed_values)
      - field_map: Dict with one source-to-target field mapping
      - allowed_values: Dict mapping source values to allowed target values

> Note:
> 1. All constraints are combined with AND logic. A row must satisfy all constraints to be kept in the result.
> 2. Field combinations are positive listings that only affect specified values. For example, if education='PhD' requires performance in [4,5], this only filters PhD records. Other education values or NULL values are not affected by this rule.
> 3. When handling NULL values in YAML or Python configurations, always use the string "pd.NA" (case-sensitive) instead of None, np.nan, or pd.NA objects to avoid unexpected behaviors.

## Examples

```python
from petsard import Constrainer


# Configure constraints
config = {
    # NaN handling rules - Specify how to handle NaN values and related fields
    'nan_groups': {
        'name': 'delete',  # Delete entire row when name is NaN
        'job': {
            'erase': ['salary', 'bonus']  # Set salary and bonus to NaN when job is NaN
        },
        'salary': {
            'copy': 'bonus'  # Copy salary value to bonus when salary has value but bonus is NaN
        }
    },

    # Field constraints - Specify value ranges for individual fields
    # Supported operators: >, >=, ==, !=, <, <=, IS, IS NOT
    # Supported logical operators: &, |
    # Supports parentheses and DATE() function
    'field_constraints': [
        "age >= 20 & age <= 60",  # Age must be between 20-60
        "performance >= 4"  # Performance must be >= 4
    ],

    # Field combination rules - Specify value mappings between different fields
    # Format: (field_map, allowed_value_pairs)
    # Note: These are positive listings, unlisted values are not filtered, for example:
    # - If education is not PhD/Master/Bachelor, it won't be filtered
    # - Only filters if education is PhD but performance is not 4 or 5
    'field_combinations': [
        (
            {'education': 'performance'},  # Education to performance mapping
            {
                'PhD': [4, 5],  # PhD only allows scores 4 or 5
                'Master': [4, 5],  # Master only allows scores 4 or 5
                'Bachelor': [3, 4, 5]  # Bachelor allows scores 3, 4, 5
            }
        ),
        # Can configure multiple field combinations
        (
            {('education', 'performance'): 'salary'},  # Education + performance to salary mapping
            {
                ('PhD', 5): [90000, 100000],  # Salary range for PhD with performance 5
                ('Master', 4): [70000, 80000]  # Salary range for Master with performance 4
            }
        )
    ]
}

cnst: Constrainer = Constrainer(config)
result: pd.DataFrame = cnst.apply(df)
```

## Methods

### `apply()`

```python
cnst.apply(df)
```

Apply configured constraints to input DataFrame.

**Parameters**

- `df` (pd.DataFrame): Input DataFrame to be constrained

**Returns**

- pd.DataFrame: DataFrame after applying all constraints

### `resample_until_satisfy()`

```python
cnst.resample_until_satisfy(
    data=df,
    target_rows=1000,
    synthesizer=synthesizer,
    postprocessor=None,
    max_trials=300,
    sampling_ratio=10.0,
    verbose_step=10
)
```

Resample data until meeting constraints with target number of rows.

**Parameters**

- `data` (pd.DataFrame): Input DataFrame to be constrained
- `target_rows` (int): Number of rows to achieve
- `synthesizer`: Synthesizer instance for generating synthetic data
- `postprocessor` (optional): Optional postprocessor for data transformation
- `max_trials` (int, default=300): Maximum number of trials before giving up
- `sampling_ratio` (float, default=10.0): Multiple of target_rows to generate in each trial
- `verbose_step` (int, default=10): Print progress every verbose_step trials

**Returns**

- pd.DataFrame: DataFrame that satisfies all constraints with target number of rows

### register()

Register a new constraint type.

**Parameters**

- `name` (str): Constraint type name
- `constraint_class` (type): Class implementing the constraint

**Returns**

None

## Attributes

- `resample_trails`: Numbers of resampling, only create after executing `resample_until_satisfy()` (int)