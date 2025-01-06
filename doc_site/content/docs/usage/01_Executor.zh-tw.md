---
title: "Executor"
draft: false
weight: 12
toc: true
---

`Executor` 介面負責協調與執行實驗。當您備好實驗設計規劃的 `yaml` 檔案後，這是您進行實驗中唯一需要使用的類別。

```Python
from petsard import Executor

filename = 'Exec_Design.yaml'
exec = Executor(config=filename)
exec.run()
```

## `Executor`

只要提供 `YAML` 格式的實驗設計檔案路徑即可初始化 `Executor`。請參考 [YAML 頁面](/petsard/zh-tw/docs/usage/02_yaml) 以了解 `YAML` 檔案的格式與內容。

```Python
exec = Executor(config)
```

**參數**

`config` (`str`): 實驗設計檔案的完整路徑。

### `run()`

執行實驗。
