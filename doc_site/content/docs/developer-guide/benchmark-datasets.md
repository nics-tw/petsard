---
title: Benchmark Dataset Maintenance
type: docs
weight: 82
prev: docs/developer-guide/development-guidelines
next: docs/developer-guide/anonymeter
---

This document explains how to maintain and extend PETsARD's benchmark dataset functionality. It is primarily intended for developers, providing guidelines for adding or modifying benchmark datasets.

## Core Concepts

The benchmark dataset system design focuses on:
- Dataset documentation maintenance
- Download and verification mechanisms
- Cache management functionality

## Dataset Documentation

### Basic Information Recording

Document the following basic information for each dataset:

- **Name**: Dataset name
- **Filename**: Filename used in the system
- **Access**: Public/private access permission
- **Columns**: Number of data columns
- **Rows**: Number of data rows
- **File Size**: File storage size
- **License**: Usage license type
- **Hash**: First seven characters of SHA-256 checksum

### Feature Information Recording

Record the feature information of datasets:

- **Too Few Samples**: Whether there are fewer than 5000 records
- **Categorical-dominant**: Whether categorical columns exceed 75%
- **Numerical-dominant**: Whether numerical columns exceed 75%
- **Non-dominant**: Whether categorical and numerical columns are balanced
- **Extreme Values**: Number of columns with extreme values
- **High Cardinality**: Number of categorical columns with high cardinality

## Verification Mechanism

### SHA256 Verification Process

Benchmark datasets use SHA256 for file integrity verification:

1. **Verification Tool**
   ```python
   from petsard.loader.benchmarker import digest_sha256


   hasher = digest_sha256(filepath)
   hash_value = hasher.hexdigest()
   ```

2. **Verification Comparison**
   - Compare the first seven characters
   - Issue warning on verification failure
   - Ensure dataset integrity

### Cache Management

Benchmark datasets use a local cache mechanism:

1. **Cache Strategy**
   - Exists and verified: Use directly
   - Does not exist: Download new file
   - Verification fails: Issue warning and stop

2. **Cache Cleanup**
   - Users can manually delete cache
   - Recommend redownload on verification failure

## Best Practices

### Dataset Selection

Consider the following when selecting datasets:
- Source reliability and stability
- Clear license terms
- Appropriate data volume
- Data quality consistency

### Maintenance Guidelines

1. **Documentation Maintenance**
   - Update dataset list promptly
   - Ensure information accuracy
   - Note important changes

2. **Data Quality**
   - Regularly check dataset availability
   - Update broken download links
   - Maintain checksum list

3. **User Experience**
   - Provide clear error messages
   - Improve usage instructions
   - Handle compatibility issues
