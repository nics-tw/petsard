---
title: 教學
type: docs
weight: 11
prev: docs/get-started
sidebar:
  open: true
---


您可以透過以下程式碼執行這些範例，只需要準備您的 YAML 設定檔：

```python
exec = Executor(config=yaml_path)
exec.run()
```

The following scenarios guide you in choosing the right YAML configuration:

1. **基本使用**: [預設合成](docs/tutorial/default-synthesis)

  - 當您只需要基本的資料合成時
  - 用於簡單的隱私強化合成資料生成

2. **基本使用與評測**: [預設合成與預設評測](docs/tutorial/default-synthesis-default-evaluation)

  - 當您需要合成與完整評測時
  - 包含保護力、保真度與實用性評估

3. **評測外部合成資料**: [外部合成與預設評測](docs/tutorial/external-synthesis-default-evaluation)

  - 當您想評估其他解決方案的合成資料時
  - 使用我們的評測指標來評估外部合成的資料

4. **特殊情境**: [特殊案例](docs/tutorial/special-cases)

  - 針對特定需求或例外情況
  - 包含獨特資料情況的解決方案

只要選擇符合您需求的情境，準備對應的 YAML 設定，即可執行上述程式碼。