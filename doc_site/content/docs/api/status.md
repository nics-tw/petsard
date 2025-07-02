---
title: Status
type: docs
weight: 64
prev: docs/api/config
next: docs/api/utils
---

```python
Status(config)
```

Advanced status management system with comprehensive progress tracking and metadata snapshot capabilities. Built on top of the Metadater architecture, Status provides complete execution history, change tracking, and state recovery mechanisms for PETsARD workflows.

## Design Overview

Status adopts a Metadater-centric architecture that provides comprehensive progress tracking and metadata management. The system maintains complete execution history through snapshots and change tracking, enabling detailed workflow analysis and state recovery.

### Key Principles

1. **Metadater-Centric**: All metadata operations are performed through the Metadater interface
2. **Complete Tracking**: Records every module execution with before/after snapshots
3. **Immutable History**: Maintains immutable execution history and change records
4. **Backward Compatibility**: Preserves all existing Status interface methods

### Architecture Components

#### 📸 Snapshot Management
```
Responsibility: Recording execution state at each step
Use Cases: Progress tracking, state recovery, debugging
Main Types: ExecutionSnapshot, SnapshotManager
```

#### 🔄 Change Tracking
```
Responsibility: Tracking metadata changes across modules
Use Cases: Change analysis, impact assessment, audit trails
Main Types: MetadataChange, ChangeTracker
```

#### 🎯 Status Management
```
Responsibility: Managing module execution status and results
Use Cases: Workflow coordination, result retrieval, state queries
Main Types: Status, StatusSummary
```

## Parameters

- `config` (Config): Configuration object containing module sequence and settings

## Core Features

### 1. Progress Snapshots
- Automatic snapshot creation before and after each module execution
- Complete metadata state capture including Schema and Field level changes
- Timestamp and execution context recording

### 2. Change Tracking
- Comprehensive tracking of metadata changes (create, update, delete)
- Schema and Field level change detection
- Change history with full audit trail

### 3. State Recovery
- Restore system state from any execution snapshot
- Incremental recovery support
- State validation and consistency checks

## Methods

### Core Status Methods (Backward Compatible)

#### `put()`

```python
status.put(module, experiment_name, operator)
```

Add module status and operator to the status dictionary with automatic snapshot creation.

**Parameters**

- `module` (str): Current module name
- `experiment_name` (str): Current experiment name  
- `operator` (BaseOperator): Current operator instance

**Enhanced Behavior**
- Creates execution snapshots automatically
- Tracks metadata changes through Metadater
- Records change history for audit trails

#### `get_result()`

```python
status.get_result(module)
```

Retrieve the result of a specific module.

**Parameters**

- `module` (str): Module name

**Returns**

- `Union[dict, pd.DataFrame]`: Module execution result

#### `get_metadata()`

```python
status.get_metadata(module="Loader")
```

Retrieve metadata for a specific module.

**Parameters**

- `module` (str, optional): Module name (default: "Loader")

**Returns**

- `SchemaMetadata`: Module metadata

#### `get_full_expt()`

```python
status.get_full_expt(module=None)
```

Retrieve experiment configuration dictionary.

**Parameters**

- `module` (str, optional): Module name filter

**Returns**

- `dict`: Module-experiment mapping

### New Snapshot and Tracking Methods

#### `get_snapshots()`

```python
status.get_snapshots(module=None)
```

Retrieve execution snapshots with optional module filtering.

**Parameters**

- `module` (str, optional): Filter by module name

**Returns**

- `List[ExecutionSnapshot]`: List of execution snapshots

#### `get_snapshot_by_id()`

```python
status.get_snapshot_by_id(snapshot_id)
```

Retrieve specific snapshot by ID.

**Parameters**

- `snapshot_id` (str): Snapshot identifier

**Returns**

- `Optional[ExecutionSnapshot]`: Snapshot object or None

#### `get_change_history()`

```python
status.get_change_history(module=None)
```

Retrieve metadata change history with optional filtering.

**Parameters**

- `module` (str, optional): Filter by module name

**Returns**

- `List[MetadataChange]`: List of change records

#### `get_metadata_evolution()`

```python
status.get_metadata_evolution(module="Loader")
```

Track metadata evolution for a specific module.

**Parameters**

- `module` (str): Module name

**Returns**

- `List[SchemaMetadata]`: Metadata evolution history

#### `restore_from_snapshot()`

```python
status.restore_from_snapshot(snapshot_id)
```

Restore system state from a specific snapshot.

**Parameters**

- `snapshot_id` (str): Snapshot identifier

**Returns**

- `bool`: Success status

#### `get_status_summary()`

```python
status.get_status_summary()
```

Get comprehensive status summary information.

**Returns**

- `Dict[str, Any]`: Status summary including:
  - `sequence`: Module execution sequence
  - `active_modules`: Currently active modules
  - `metadata_modules`: Modules with metadata
  - `total_snapshots`: Total snapshot count
  - `total_changes`: Total change record count
  - `last_snapshot`: Most recent snapshot ID
  - `last_change`: Most recent change ID

## Data Types

### ExecutionSnapshot

```python
@dataclass(frozen=True)
class ExecutionSnapshot:
    snapshot_id: str
    module_name: str
    experiment_name: str
    timestamp: datetime
    metadata_before: Optional[SchemaMetadata]
    metadata_after: Optional[SchemaMetadata]
    execution_context: Dict[str, Any]
```

Immutable snapshot of module execution state.

### MetadataChange

```python
@dataclass(frozen=True)
class MetadataChange:
    change_id: str
    change_type: str  # 'create', 'update', 'delete'
    target_type: str  # 'schema', 'field'
    target_id: str
    before_state: Optional[Any]
    after_state: Optional[Any]
    timestamp: datetime
    module_context: str
```

Immutable record of metadata changes.

## Usage Examples

### Basic Usage (Backward Compatible)

```python
from petsard.config import Config
from petsard.status import Status

# Create configuration
config_dict = {
    "Loader": {"data": {"filepath": "benchmark://adult-income"}},
    "Synthesizer": {"demo": {"method": "default"}},
    "Reporter": {"output": {"method": "save_data", "source": "Synthesizer"}}
}

config = Config(config_dict)
status = Status(config)

# Traditional usage (unchanged)
# status.put(module, experiment, operator)  # Called by Executor
result = status.get_result("Loader")
metadata = status.get_metadata("Loader")
```

### Advanced Snapshot Tracking

```python
# Get all execution snapshots
snapshots = status.get_snapshots()
print(f"Total snapshots: {len(snapshots)}")

# Get snapshots for specific module
loader_snapshots = status.get_snapshots("Loader")
for snapshot in loader_snapshots:
    print(f"Snapshot: {snapshot.snapshot_id}")
    print(f"Module: {snapshot.module_name}")
    print(f"Timestamp: {snapshot.timestamp}")

# Get specific snapshot
snapshot = status.get_snapshot_by_id("snapshot_000001_20241224_210000")
if snapshot:
    print(f"Execution context: {snapshot.execution_context}")
```

### Change Tracking and Analysis

```python
# Get all metadata changes
changes = status.get_change_history()
print(f"Total changes: {len(changes)}")

# Analyze changes by module
loader_changes = status.get_change_history("Loader")
for change in loader_changes:
    print(f"Change: {change.change_type} {change.target_type}")
    print(f"Target: {change.target_id}")
    print(f"Context: {change.module_context}")

# Track metadata evolution
evolution = status.get_metadata_evolution("Loader")
print(f"Metadata versions: {len(evolution)}")
```

### Status Summary and Diagnostics

```python
# Get comprehensive status summary
summary = status.get_status_summary()
print(f"Active modules: {summary['active_modules']}")
print(f"Total snapshots: {summary['total_snapshots']}")
print(f"Total changes: {summary['total_changes']}")
print(f"Last snapshot: {summary['last_snapshot']}")

# Check execution sequence
print(f"Module sequence: {summary['sequence']}")
```

### State Recovery

```python
# List available snapshots
snapshots = status.get_snapshots()
for snapshot in snapshots[-5:]:  # Last 5 snapshots
    print(f"{snapshot.snapshot_id}: {snapshot.module_name}[{snapshot.experiment_name}]")

# Restore from specific snapshot
success = status.restore_from_snapshot("snapshot_000003_20241224_210500")
if success:
    print("State restored successfully")
else:
    print("State restoration failed")
```

## Architecture Benefits

### 1. Metadater Integration
- **Unified Metadata Management**: All metadata operations through Metadater interface
- **Consistent Data Types**: Uses SchemaMetadata and FieldMetadata throughout
- **Type Safety**: Strong typing with immutable data structures

### 2. Complete Observability
- **Execution Tracking**: Complete history of module executions
- **Change Auditing**: Full audit trail of metadata changes
- **State Snapshots**: Point-in-time state capture for recovery

### 3. Backward Compatibility
- **Preserved Interface**: All existing Status methods unchanged
- **Seamless Migration**: No code changes required for existing workflows
- **Enhanced Functionality**: New features available without breaking changes

### 4. Performance Optimization
- **Efficient Storage**: Immutable data structures with structural sharing
- **Lazy Loading**: Snapshots loaded on-demand
- **Memory Management**: Automatic cleanup of old snapshots

## Migration Guide

### From Legacy Status

The new Status is fully backward compatible. Existing code continues to work unchanged:

```python
# Existing code (no changes needed)
status.put(module, experiment, operator)
result = status.get_result(module)
metadata = status.get_metadata(module)

# New features (optional)
snapshots = status.get_snapshots()
changes = status.get_change_history()
summary = status.get_status_summary()
```

### Enhanced Workflows

```python
# Enhanced workflow with tracking
def enhanced_workflow(status):
    # Execute modules (existing logic)
    # ...
    
    # New: Analyze execution history
    summary = status.get_status_summary()
    if summary['total_changes'] > 0:
        print(f"Detected {summary['total_changes']} metadata changes")
    
    # New: Create recovery point
    snapshots = status.get_snapshots()
    if snapshots:
        latest_snapshot = snapshots[-1]
        print(f"Recovery point: {latest_snapshot.snapshot_id}")
```

This enhanced Status system provides comprehensive workflow tracking and state management while maintaining full compatibility with existing PETsARD workflows.