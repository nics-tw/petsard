---
title: 自定義合成
type: docs
weight: 31
prev: docs/tutorial/use-cases/comparing-synthesizers
next: docs/tutorial/use-cases/data-constraining
---


除了使用內建的合成方法外，您也可以建立自己的合成方法。這在您有特定的合成需求時特別有用。

請點擊下方按鈕在 Colab 中執行範例：

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/nics-tw/petsard/blob/main/demo/use-cases/custom-synthesis.ipynb)

```yaml
---
Loader:
  data:
    filepath: 'benchmark://adult-income'
Preprocessor:
  demo:
    method: 'default'
Synthesizer:
  custom:
    method: 'custom_method'
    module_path: 'custom-synthesis.py'  # 自定義合成器的路徑
    class_name: 'MySynthesizer_Shuffle' # 合成器類別名稱
Postprocessor:
  demo:
    method: 'default'
Evaluator:
  demo:
    method: 'default'
Reporter:
  save_report_global:
    method: 'save_report'
    granularity: 'global'
...
```

## 建立自定義合成器

建立一個實作必要方法的合成器類別：

```python
import numpy as np
import pandas as pd

from petsard.metadater import SchemaMetadata


class MySynthesizer_Shuffle:
    """
    一個簡單的合成器，獨立地隨機排列每個欄位。

    這個合成器保留每個欄位的分佈，同時打破欄位之間的關係。
    這對於簡單的匿名化或作為基準合成資料生成方法很有用。
    """

    def __init__(self, config: dict, metadata: SchemaMetadata):
        """
        初始化合成器。

        在這個示範中我們不使用 metadata，但請保留它在簽名中，
        並且歡迎準備您的合成器使用它。

        Args:
            metadata (SchemaMetadata): 元數據物件。
        """
        self.config: dict = config
        self.result: pd.DataFrame = None

        if "random_seed" in self.config:
            np.random.seed(self.config["random_seed"])

    def fit(self, data: pd.DataFrame) -> None:
        """
        隨機排列演算法
        """
        if not isinstance(data, pd.DataFrame):
            raise TypeError("資料必須是 pandas DataFrame")

        if data.empty:
            raise ValueError("無法訓練空資料")

        columns: list[str] = data.columns.tolist()
        synthetic_data: pd.DataFrame = pd.DataFrame()

        values: np.ndarray = None
        for col in columns:
            # 獲取欄位數據並適當處理不同類型
            original_series: pd.Series = data[col]

            if pd.api.types.is_categorical_dtype(original_series):
                # 對於分類數據，轉換為代碼，隨機排列，然後映射回來
                codes = original_series.cat.codes.values.copy()
                np.random.shuffle(codes)
                # 將隨機排列的代碼轉換回分類值
                synthetic_data[col] = pd.Categorical.from_codes(
                    codes,
                    categories=original_series.cat.categories,
                    ordered=original_series.cat.ordered,
                )
            else:
                # 對於非分類數據，創建值的副本並隨機排列
                values = original_series.values.copy()
                np.random.shuffle(values)
                synthetic_data[col] = values

        self.result = synthetic_data

    def sample(self) -> pd.DataFrame:
        return self.result
```

## 必要實作方法

您的合成器類別必須實作以下所有方法：

1. `__init__(config: dict, metadata: SchemaMetadata)`：初始化合成器

    - 接收配置字典和元數據物件
    - 設置任何必要的參數或內部狀態

2. `fit(data: pd.DataFrame)`：使用輸入資料訓練合成器

    - 處理輸入資料並準備合成
    - 學習模式、分佈或關係

3. `sample()`：生成合成資料

    - 回傳包含合成資料的 pandas DataFrame
    - 應維持與原始資料相同的結構

所有三個方法都必須實作，自定義合成器才能與 PETsARD 正確運作。合成器預期會生成維持原始資料結構的合成資料，同時應用您的自定義合成演算法。
