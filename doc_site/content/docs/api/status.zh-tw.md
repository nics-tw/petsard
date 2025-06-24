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

進階狀態管理系統，具備完整的進度追蹤和詮釋資料快照功能。建構於 Metadater 架構之上，Status 為 PETsARD 工作流程提供完整的執行歷史、變更追蹤和狀態恢復機制。

## 設計概覽

Status 採用以 Metadater 為中心的架構，提供全面的進度追蹤和詮釋資料管理。系統透過快照和變更追蹤維護完整的執行歷史，支援詳細的工作流程分析和狀態恢復。

### 核心原則

1. **以 Metadater 為中心**：所有詮釋資料操作都透過 Metadater 介面執行
2. **完整追蹤**：記錄每個模組執行的前後快照
3. **不可變歷史**：維護不可變的執行歷史和變更記錄
4. **向後相容**：保留所有現有的 Status 介面方法

### 架構元件

#### 📸 快照管理
```
職責：記錄每個步驟的執行狀態
使用場景：進度追蹤、狀態恢復、除錯
主要類型：ExecutionSnapshot、SnapshotManager
```

#### 🔄 變更追蹤
```
職責：追蹤跨模組的詮釋資料變更
使用場景：變更分析、影響評估、稽核軌跡
主要類型：MetadataChange、ChangeTracker
```

#### 🎯 狀態管理
```
職責：管理模組執行狀態和結果
使用場景：工作流程協調、結果檢索、狀態查詢
主要類型：Status、StatusSummary
```

## 參數

- `config` (Config)：包含模組序列和設定的配置物件

## 核心功能

### 1. 進度快照
- 在每個模組執行前後自動建立快照
- 完整的詮釋資料狀態擷取，包括 Schema 和 Field 層級的變更
- 時間戳和執行上下文記錄

### 2. 變更追蹤
- 全面追蹤詮釋資料變更（建立、更新、刪除）
- Schema 和 Field 層級的變更偵測
- 具有完整稽核軌跡的變更歷史

### 3. 狀態恢復
- 從任何執行快照恢復系統狀態
- 支援增量恢復
- 狀態驗證和一致性檢查

## 方法

### 核心狀態方法（向後相容）

#### `put()`

```python
status.put(module, experiment_name, operator)
```

將模組狀態和操作器新增到狀態字典，並自動建立快照。

**參數**

- `module` (str)：當前模組名稱
- `experiment_name` (str)：當前實驗名稱
- `operator` (BaseOperator)：當前操作器實例

**增強行為**
- 自動建立執行快照
- 透過 Metadater 追蹤詮釋資料變更
- 記錄變更歷史以供稽核

#### `get_result()`

```python
status.get_result(module)
```

檢索特定模組的結果。

**參數**

- `module` (str)：模組名稱

**回傳**

- `Union[dict, pd.DataFrame]`：模組執行結果

#### `get_metadata()`

```python
status.get_metadata(module="Loader")
```

檢索特定模組的詮釋資料。

**參數**

- `module` (str, optional)：模組名稱（預設："Loader"）

**回傳**

- `SchemaMetadata`：模組詮釋資料

#### `get_full_expt()`

```python
status.get_full_expt(module=None)
```

檢索實驗配置字典。

**參數**

- `module` (str, optional)：模組名稱篩選器

**回傳**

- `dict`：模組-實驗對應關係

### 新的快照和追蹤方法

#### `get_snapshots()`

```python
status.get_snapshots(module=None)
```

檢索執行快照，可選擇性地按模組篩選。

**參數**

- `module` (str, optional)：按模組名稱篩選

**回傳**

- `List[ExecutionSnapshot]`：執行快照列表

#### `get_snapshot_by_id()`

```python
status.get_snapshot_by_id(snapshot_id)
```

根據 ID 檢索特定快照。

**參數**

- `snapshot_id` (str)：快照識別碼

**回傳**

- `Optional[ExecutionSnapshot]`：快照物件或 None

#### `get_change_history()`

```python
status.get_change_history(module=None)
```

檢索詮釋資料變更歷史，可選擇性篩選。

**參數**

- `module` (str, optional)：按模組名稱篩選

**回傳**

- `List[MetadataChange]`：變更記錄列表

#### `get_metadata_evolution()`

```python
status.get_metadata_evolution(module="Loader")
```

追蹤特定模組的詮釋資料演進。

**參數**

- `module` (str)：模組名稱

**回傳**

- `List[SchemaMetadata]`：詮釋資料演進歷史

#### `restore_from_snapshot()`

```python
status.restore_from_snapshot(snapshot_id)
```

從特定快照恢復系統狀態。

**參數**

- `snapshot_id` (str)：快照識別碼

**回傳**

- `bool`：成功狀態

#### `get_status_summary()`

```python
status.get_status_summary()
```

取得全面的狀態摘要資訊。

**回傳**

- `Dict[str, Any]`：狀態摘要，包括：
  - `sequence`：模組執行序列
  - `active_modules`：目前活躍的模組
  - `metadata_modules`：具有詮釋資料的模組
  - `total_snapshots`：總快照數量
  - `total_changes`：總變更記錄數量
  - `last_snapshot`：最新快照 ID
  - `last_change`：最新變更 ID

## 資料類型

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

模組執行狀態的不可變快照。

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

詮釋資料變更的不可變記錄。

## 使用範例

### 基本使用（向後相容）

```python
from petsard.config import Config
from petsard.status import Status

# 建立配置
config_dict = {
    "Loader": {"data": {"filepath": "benchmark://adult-income"}},
    "Synthesizer": {"demo": {"method": "default"}},
    "Reporter": {"output": {"method": "save_data", "source": "Synthesizer"}}
}

config = Config(config_dict)
status = Status(config)

# 傳統使用方式（不變）
# status.put(module, experiment, operator)  # 由 Executor 呼叫
result = status.get_result("Loader")
metadata = status.get_metadata("Loader")
```

### 進階快照追蹤

```python
# 取得所有執行快照
snapshots = status.get_snapshots()
print(f"總快照數量：{len(snapshots)}")

# 取得特定模組的快照
loader_snapshots = status.get_snapshots("Loader")
for snapshot in loader_snapshots:
    print(f"快照：{snapshot.snapshot_id}")
    print(f"模組：{snapshot.module_name}")
    print(f"時間戳：{snapshot.timestamp}")

# 取得特定快照
snapshot = status.get_snapshot_by_id("snapshot_000001_20241224_210000")
if snapshot:
    print(f"執行上下文：{snapshot.execution_context}")
```

### 變更追蹤和分析

```python
# 取得所有詮釋資料變更
changes = status.get_change_history()
print(f"總變更數量：{len(changes)}")

# 按模組分析變更
loader_changes = status.get_change_history("Loader")
for change in loader_changes:
    print(f"變更：{change.change_type} {change.target_type}")
    print(f"目標：{change.target_id}")
    print(f"上下文：{change.module_context}")

# 追蹤詮釋資料演進
evolution = status.get_metadata_evolution("Loader")
print(f"詮釋資料版本：{len(evolution)}")
```

### 狀態摘要和診斷

```python
# 取得全面的狀態摘要
summary = status.get_status_summary()
print(f"活躍模組：{summary['active_modules']}")
print(f"總快照數量：{summary['total_snapshots']}")
print(f"總變更數量：{summary['total_changes']}")
print(f"最新快照：{summary['last_snapshot']}")

# 檢查執行序列
print(f"模組序列：{summary['sequence']}")
```

### 狀態恢復

```python
# 列出可用的快照
snapshots = status.get_snapshots()
for snapshot in snapshots[-5:]:  # 最後 5 個快照
    print(f"{snapshot.snapshot_id}: {snapshot.module_name}[{snapshot.experiment_name}]")

# 從特定快照恢復
success = status.restore_from_snapshot("snapshot_000003_20241224_210500")
if success:
    print("狀態恢復成功")
else:
    print("狀態恢復失敗")
```

## 架構優勢

### 1. Metadater 整合
- **統一詮釋資料管理**：所有詮釋資料操作都透過 Metadater 介面
- **一致的資料類型**：全程使用 SchemaMetadata 和 FieldMetadata
- **類型安全**：使用不可變資料結構的強類型

### 2. 完整可觀測性
- **執行追蹤**：完整的模組執行歷史
- **變更稽核**：詮釋資料變更的完整稽核軌跡
- **狀態快照**：用於恢復的時間點狀態擷取

### 3. 向後相容性
- **保留介面**：所有現有的 Status 方法不變
- **無縫遷移**：現有工作流程無需程式碼變更
- **增強功能**：新功能可用且不會破壞現有功能

### 4. 效能最佳化
- **高效儲存**：具有結構共享的不可變資料結構
- **延遲載入**：按需載入快照
- **記憶體管理**：自動清理舊快照

## 遷移指南

### 從舊版 Status

新的 Status 完全向後相容。現有程式碼可以繼續正常運作：

```python
# 現有程式碼（無需變更）
status.put(module, experiment, operator)
result = status.get_result(module)
metadata = status.get_metadata(module)

# 新功能（可選）
snapshots = status.get_snapshots()
changes = status.get_change_history()
summary = status.get_status_summary()
```

### 增強工作流程

```python
# 具有追蹤功能的增強工作流程
def enhanced_workflow(status):
    # 執行模組（現有邏輯）
    # ...
    
    # 新功能：分析執行歷史
    summary = status.get_status_summary()
    if summary['total_changes'] > 0:
        print(f"偵測到 {summary['total_changes']} 個詮釋資料變更")
    
    # 新功能：建立恢復點
    snapshots = status.get_snapshots()
    if snapshots:
        latest_snapshot = snapshots[-1]
        print(f"恢復點：{latest_snapshot.snapshot_id}")
```

這個增強的 Status 系統提供全面的工作流程追蹤和狀態管理，同時與現有的 PETsARD 工作流程保持完全相容性。