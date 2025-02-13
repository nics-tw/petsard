---
title: 教學
type: docs
weight: 10
prev: docs/get-started
next: docs/best-practices
sidebar:
  open: false
---


您可以透過以下程式碼執行這些範例，只需要準備您的 YAML 設定檔：

```python
exec = Executor(config=yaml_path)
exec.run()
```

以下情境可以幫助您選擇合適的 YAML 設定方式：

1. **YAML 設定：[YAML 設定](./yaml-config)**

   - 當您需要了解如何設定實驗參數時
   - 用於管理和組織複雜的實驗流程
   - 透過 YAML 檔案控制所有實驗設定

2. **基本使用：[預設合成](./default-synthesis)**

  - 當您只需要基本的資料合成時
  - 用於簡單的隱私強化合成資料生成

3. **資料約束：[資料約束](./data-constraining)**

  - 當您需要控制合成資料的特性時
  - 包含欄位值規則、欄位組合和空值處理
  - 確保合成資料符合業務邏輯

4. **基本使用與評測：[預設合成與預設評測](./default-synthesis-default-evaluation)**

  - 當您需要合成與完整評測時
  - 包含保護力、保真度與實用性評估

5. **評測外部合成資料：[外部合成與預設評測](./external-synthesis-default-evaluation)**

  - 當您想評估其他解決方案的合成資料時
  - 使用我們的評測指標來評估外部合成的資料

6. **特殊情境**：[使用案例](./use-cases)

  - 探索不同的合成應用場景
  - 處理各種實務需求
  - 提供實測過的流程解決方案

只要選擇符合您需求的情境，準備對應的 YAML 設定，即可執行上述程式碼。