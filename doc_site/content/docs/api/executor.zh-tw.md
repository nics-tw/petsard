---
title: Executor
type: docs
weight: 51
prev: docs/api
next: docs/api/loader
---


```python
Executor(
    config=None
)
```

實驗管線的執行器，根據設定檔執行一系列的操作。

## 參數

- `config` (str)：設定檔名稱

## 範例

```python
exec = Executor(config=yaml_path)
exec.run()
```

## 方法

### `run()`

根據設定檔執行實驗管線。

**參數**

無

**回傳值**

無。執行結果儲存於 `result` 屬性

### `get_result()`

取得實驗結果。

**參數**

無

**回傳值**

- dict：包含所有實驗結果的字典
  - 格式：`{full_expt_name: result}`

## 屬性

- `config`：設定檔內容（Config 物件）
- `sequence`：執行順序列表
- `status`：執行狀態（Status 物件）
- `result`：執行結果字典