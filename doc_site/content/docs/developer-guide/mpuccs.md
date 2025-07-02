---
title: mpUCCs Experimental Feature
type: docs
weight: 85
prev: docs/developer-guide/anonymeter
next: docs/developer-guide/logging-configuration
math: true
---

## Overview

mpUCCs (Maximal Partial Unique Column Combinations) is an experimental privacy risk assessment tool in the PETsARD system, based on the theory of maximal partial unique column combinations, providing more accurate and efficient privacy risk assessment than traditional singling-out attack methods.

Click the below button to run this example in Colab:

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/nics-tw/petsard/blob/main/demo/developer-guide/mpuccs.ipynb)

```yaml
---
Loader:
  data:
    filepath: 'benchmark/adult-income.csv'
Splitter:
  demo:
    num_samples: 1
    train_split_ratio: 0.8
Preprocessor:
  demo:
    method: 'default'
Synthesizer:
  demo:
    method: 'default'
Postprocessor:
  demo:
    method: 'default'
Evaluator:
  demo-mpuccs:
    method: 'mpuccs'
    n_cols:
      - 1
      - 2
      - 3
      - 4
      - 5
Reporter:
  output:
    method: 'save_data'
    source: 'Synthesizer'
  save_report_global:
    method: 'save_report'
    granularity: 'global'
...
```

## Theoretical Foundation

### Core Concepts

#### UCC (Unique Column Combinations)
UCC refers to field combinations where all values are unique across all records in the dataset, with no duplicates.

**Example:**
For address data, the address is a unique value. The address can also be viewed as a unique combination of county, township, road, and house number.

#### pUCC (Partial Unique Column Combinations)
pUCC refers to combinations that are unique only under specific conditions or specific values, not unique across the entire dataset.

**Example:**
In most cases, street names and house numbers are not unique because there are many streets with the same name in different townships. Only (1.) special road names or (2.) special house numbers are unique values.

#### mpUCCs (Maximal Partial Unique Column Combinations)
mpUCCs refer to pUCCs in maximal form, meaning there is no smaller subset that can achieve the same identification effect.

**Example:**
For "Zhongxiao East Road" "Section 1" "No. 1", since other counties also have Zhongxiao East Road, removing any field attribute cannot achieve unique identification, which is mpUCCs.

### Key Theoretical Insights

#### mpUCCs = QIDs (Quasi-identifiers)
The essence of singling-out attacks is:
1. Identify a unique field combination in synthetic data
2. This combination also corresponds to a unique record in original data

This is essentially equivalent to finding pUCCs and then checking for collisions.

#### Self-contained Anonymity
When a dataset has no feature combinations (IDs + QIDs) that can uniquely identify original entities, the dataset is considered anonymized.

**Finding QIDs (Find-QIDs problem) is equivalent to discovering mpUCCs!**

Repeatedly calculating non-maximal field combinations will overestimate risk - this is the negative expression of the set-theoretic meaning of singling-out risk!

## Algorithm Implementation

### Challenges of Find-QIDs Problem

1. For k attributes, potential QIDs are 2^k - 1 combinations
2. Proven to be a W[2]-complete problem (Bläsius et al., 2017)
3. The problem lacks optimal substructure, so dynamic programming cannot be applied

**Example:** Knowing that {A, B} and {B, C} have no pUCCs does not mean {A, B, C} has none.

### Our Solution: Heuristic Greedy Cardinality-Prioritized Algorithm

#### 1. High-Cardinality Field Priority
- Calculate cardinality of all fields
- For numeric fields, round to lowest precision
- Process field combinations breadth-first: few to many, high cardinality first

#### 2. Set Operations on Field and Value Domain Combinations
- Use `collections.Counter` to capture value domain combinations with only one occurrence in synthetic data
- Compare to find the same value domain combinations with only one occurrence in original data
- Record corresponding original and synthetic data indices

#### 3. Pruning Strategy
If all value domain combinations of a field combination are unique and colliding, skip its supersets.

#### 4. Masking Mechanism
For synthetic data already identified by high-cardinality few-field combinations, that row no longer collides.

#### 5. Early Stopping Based on Conditional Entropy
We propose an algorithm based on functional dependency entropy research (Mandros et al., 2020):

**For field combinations with k ≥ 2:**

1. **Field Combination Entropy** H(XY) = entropy(Counter(syn_data[XY]) / syn_n_rows)
2. **Conditional Entropy** H(Y|X) = Σ p(X = x)*H(Y | X = x), where x ∈ {pUCC, ¬pUCC}
3. **Mutual Information** I(X; Y) = H(Y) - H(Y|X)

**Early Stopping:** If mutual information is negative, subsequent inherited field combinations are no longer confirmed.

#### 6. Rényi Entropy (α=2, Collision Entropy)
We use Rényi entropy instead of Shannon entropy for better collision probability analysis:

- **Theoretical Maximum Entropy** = log(n_rows)
- **Synthetic Data Maximum Entropy** = scipy.stats.entropy(Counter(syn_data))
- **Field Combination Entropy** = scipy.stats.entropy(Counter(syn_data[column_combos]))
- **Normalization** = Synthetic Data Maximum Entropy - Field Combination Entropy

## Key Improvements Over Anonymeter

### 1. Theoretical Foundation
- **Clear theoretical basis**: mpUCCs = QIDs provides solid mathematical foundation
- **Avoids risk overestimation**: Focuses on maximal combinations only
- **Set-theoretic meaning**: Proper understanding of singling-out risk

### 2. Algorithm Optimization
- **Progressive tree-based search**: Efficient field combination exploration
- **Entropy-based pruning**: Intelligent early stopping mechanism
- **Cardinality-prioritized processing**: High-cardinality fields processed first
- **Collision-focused analysis**: Direct focus on actual privacy risks

### 3. Precision Handling
- **Automatic numeric precision detection**: Handles floating-point comparisons
- **Datetime precision support**: Handles temporal data appropriately
- **Manual precision override**: Allows custom precision settings

### 4. Performance Improvements
- **Faster execution**: 5 minutes vs 12+ minutes on adult-income dataset
- **Better scalability**: Efficient handling of high-dimensional data
- **Memory optimization**: Counter-based uniqueness detection

### 5. Comprehensive Progress Tracking
- **Dual-layer progress bars**: Field-level and combination-level progress
- **Detailed execution tree**: Complete audit trail of algorithm decisions
- **Pruning statistics**: Transparency in optimization decisions

## Configuration Parameters

```python
config = {
    'eval_method': 'mpuccs',
    'n_cols': None,                    # Target combination sizes (None/int/list)
    'min_entropy_delta': 0.0,          # Minimum entropy gain threshold
    'field_decay_factor': 0.5,         # Field decay factor for weighting
    'renyi_alpha': 2.0,                # Rényi entropy parameter (collision entropy)
    'numeric_precision': None,          # Numeric precision (auto-detect or manual)
    'datetime_precision': None          # Datetime precision (auto-detect or manual)
}
```

### Parameter Details

#### `n_cols`
- `None`: Evaluate all combination sizes from 1 to number of fields
- `int`: Evaluate only specific combination size
- `list`: Evaluate specific combination sizes (supports skip patterns like [1, 3])

#### `min_entropy_delta`
- Minimum entropy gain required to continue exploring a branch
- Any positive value means pruning occurs when there is any entropy difference
- Higher values lead to more aggressive pruning
- Default: 0.0 (no entropy-based pruning)

#### `field_decay_factor`
- Weighting factor for larger field combinations
- Reflects the practical difficulty of using more fields in attacks
- Default: 0.5 (each additional field halves the weight)

#### `renyi_alpha`
- Alpha parameter for Rényi entropy calculation
- α=2 corresponds to collision entropy, suitable for privacy analysis
- Default: 2.0

## Usage Examples

### Basic Usage
```python
from petsard.evaluator import Evaluator

# Initialize evaluator
evaluator = Evaluator('mpuccs')
evaluator.create()

# Evaluate privacy risk
results = evaluator.eval({
    'ori': original_data,
    'syn': synthetic_data
})

# Access results
global_stats = results['global']
detailed_results = results['details']
tree_analysis = results['tree']
```

### Advanced Configuration
```python
# Custom configuration
evaluator = Evaluator('mpuccs', 
                     n_cols=[1, 2, 3],           # Only 1, 2, 3 field combinations
                     min_entropy_delta=0.1,      # Aggressive pruning
                     field_decay_factor=0.3,     # Strong decay for large combinations
                     numeric_precision=2)         # 2 decimal places for numbers

evaluator.create()
results = evaluator.eval({
    'ori': original_data,
    'syn': synthetic_data
})
```

### Skip Pattern Configuration
```python
# Skip 2-field combinations, only evaluate 1 and 3-field combinations
evaluator = Evaluator('mpuccs', n_cols=[1, 3])
evaluator.create()
results = evaluator.eval({
    'ori': original_data,
    'syn': synthetic_data
})
```

## Output Results

### Global Results
```python
{
    'total_syn_records': 1000,              # Total synthetic records
    'total_ori_records': 1000,              # Total original records  
    'total_identified': 150,                # Successfully identified records
    'identification_rate': 0.15,            # Basic identification rate
    'weighted_identification_rate': 0.12,   # Weighted identification rate
    'total_combinations_checked': 45,       # Total combinations evaluated
    'total_combinations_pruned': 12,        # Combinations pruned by algorithm
    'config_n_cols': '[1, 2, 3]',          # Configuration used
    'config_min_entropy_delta': 0.1,       # Entropy threshold used
    'config_field_decay_factor': 0.5,      # Decay factor used
    'config_renyi_alpha': 2.0,             # Rényi alpha parameter
    'config_numeric_precision': 2,          # Numeric precision applied
    'config_datetime_precision': 'D'        # Datetime precision applied
}
```

### Details Results
```python
[
    {
        'combo_size': 2,                    # Number of fields in combination
        'syn_idx': 42,                      # Synthetic data index
        'field_combo': "('age', 'income')", # Field combination used
        'value_combo': "(25, 50000)",       # Values that caused collision
        'ori_idx': 123                      # Corresponding original data index
    },
    # ... more collision records
]
```

### Tree Results
```python
[
    {
        'check_order': 1,                   # Processing order
        'combo_size': 2,                    # Combination size
        'field_combo': "('age', 'income')", # Field combination
        'base_combo': "('age',)",           # Base combination for entropy calculation
        'base_is_pruned': False,            # Whether base was pruned
        'combo_entropy': 0.85,              # Normalized Rényi entropy
        'base_entropy': 0.72,               # Base combination entropy
        'entropy_gain': 0.13,               # Entropy gain from base
        'is_pruned': False,                 # Whether this combination was pruned
        'mpuccs_cnt': 5,                    # Number of unique combinations found
        'mpuccs_collision_cnt': 3,          # Number of successful collisions
        'field_weighted': 0.5,              # Field-based weighting
        'total_weighted': 0.5,              # Total weighting applied
        'weighted_mpuccs_collision_cnt': 1.5 # Weighted collision count
    },
    # ... more tree nodes
]
```

## Performance Characteristics

### Computational Complexity
- **Time Complexity**: O(2^k) in worst case, but with significant pruning
- **Space Complexity**: O(n*k) where n is number of records, k is number of fields
- **Practical Performance**: Linear to sub-quadratic on real datasets due to pruning

### Scalability
- **Field Scalability**: Highly scalable with pruning - can handle datasets with many fields efficiently
- **Record Scalability**: Tested on datasets with 100K+ records
- **Memory Efficiency**: Counter-based operations minimize memory usage

### Comparison with Anonymeter
| Metric | Anonymeter | mpUCCs | Improvement |
|--------|------------|--------|-------------|
| Execution Time (adult-income, n_cols=3) | 12+ minutes | 44 seconds | 16x faster |
| Singling-out Detection | ~1,000-2,000 (random sampling) | 7,999 (complete evaluation) | Complete coverage |
| Theoretical Foundation | Heuristic | Mathematical | Solid theory |
| Risk Overestimation | High | Low | Accurate assessment |
| Progress Visibility | Not supported | Comprehensive | Full transparency |
| Precision Handling | Not supported | Automatic | Better usability |

## Best Practices

### 1. Configuration Selection
- Use default settings for optimal results

### 2. Data Preprocessing
- Ensure consistent data types between original and synthetic data
- Consider appropriate precision for numeric and datetime fields
- Remove or handle missing values consistently

### 3. Result Interpretation
- Focus on `weighted_identification_rate` for practical risk assessment
- Examine `details` results to understand specific vulnerabilities
- Use `tree` results to understand algorithm decisions and optimization

### 4. Performance Optimization
- Use skip patterns (`n_cols=[1, 3]`) to focus on specific combination sizes
- Consider field selection to reduce dimensionality if needed

## Limitations and Future Work

### Current Limitations
1. **Experimental Status**: Still under active development and validation
2. **Memory Usage**: Can be memory-intensive for very high-dimensional data
3. **Risk Weighting**: Theoretically sound risk weighting methods are under research, currently using field_decay_factor = 0.5

### Future Enhancements
1. **Distributed Computing**: Support for parallel processing of large datasets (nice-to-have)

## References

1. Abedjan, Z., & Naumann, F. (2011). Advancing the discovery of unique column combinations. In Proceedings of the 20th ACM international conference on Information and knowledge management (pp. 1565-1570).

2. Mandros, P., Kaltenpoth, D., Boley, M., & Vreeken, J. (2020). Discovering Functional Dependencies from Mixed-Type Data. In Proceedings of the 26th ACM SIGKDD International Conference on Knowledge Discovery & Data Mining (pp. 1404-1414).

3. Bläsius, T., Friedrich, T., Lischeid, J., Meeks, K., & Schirneck, M. (2017). Efficiently enumerating hitting sets of hypergraphs arising in data profiling. In Proceedings of the 16th International Symposium on Experimental Algorithms (pp. 130-145).

## Support and Feedback

As an experimental feature, mpUCCs is actively being developed and improved. We welcome feedback, bug reports, and suggestions for enhancement. Please refer to the project's issue tracker for reporting problems or requesting features.