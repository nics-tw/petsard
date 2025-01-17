---
title: "User Story"
draft: false
weight: 14
toc: true
---

用戶故事的示範旨在協助使用者設定您自身的設定檔案。祝您使用愉快 : )

建議搭配 GitHub 倉儲中 [demo/README.md](https://github.com/nics-tw/petsard/tree/main/demo) 的 `demo/用戶故事 A/B/C/D.ipynb` 用戶故事情境範例、與 [yaml/README.md](https://github.com/nics-tw/petsard/tree/main/yaml)，幫助釐清您的需求如何實現。

### 環境

在 `PETsARD` 中，您唯一所需要做的，便是參考範例準備 YAML 檔案，並執行 `Executor`。

假設您的 YAML 檔案名稱為 `config.yaml`，則您的 Python 程式碼為：

```Python
exec = Executor(config='config.yaml')
exec.run()
```

## 用戶故事 A

**隱私強化資料合成**

本示範將展示如何使用 `PETsARD` 合成隱私強化資料。

在這個示範中，您作為使用者，在本機上已經擁有一份資料檔案，而 `PETsARD` 將幫助您讀取該檔案、然後合成經隱私強化後的版本。

同時，隱私強化演算法通常都有特定資料格式、以及特定資料處理程序的限制，`PETsARD` 已經為使用者考慮到這點，`PETsARD` 提供預設與可客製化的前後處理流程，幫助使用者快速上手。

### 用戶故事 A-1

**預設合成流程**

給定一個原始資料集、但未指定演算法，該流程會利用預設的演算法合成一組隱私強化資料集。

### 用戶故事 A-2

**自訂合成流程**

給定一個原始資料集，並指定隱私強化技術合成演算法與參數，該流程會依此產生隱私強化資料集。

## 用戶故事 B

**隱私強化資料合成與評測**

本示範將展示如何使用 `PETsARD` 合成與評測隱私強化資料。

在這個示範中，您作為使用者，在本機上已經擁有一份資料檔案，而 `PETsARD` 將幫助您讀取該檔案、合成經隱私強化後的版本、最終評測。

### 用戶故事 B-1

**預設評測流程**

根據用戶故事 A，如果使用者啟用了 'evaluate' 步驟，評估模組會產生涵蓋預設的隱私風險與效用指標的報告。

### 用戶故事 B-2

**自訂預設評測流程**

根據用戶故事 B-1，如果指定特定的指標、或是提供用戶自定義的評估腳本，模組會產生客製化的評估報告。

## 用戶故事 C

**隱私強化資料評測**

本示範將展示如何使用 `PETsARD` 評測隱私強化資料。

在這個示範中，您作為使用者，在本機上已經擁有一份資料檔案、以及其對應的合成資料結果，這很可能是來自於您現有的隱私保護服務，而 `PETsARD` 將幫助您讀取這些檔案、評測結果，幫助您針對現有的解決方案跟其他技術做比較。

### 用戶故事 C-1

**描述流程**

給定一個資料集做輸入，該流程可以藉由調用 'describe' 模組而得到該資料集的摘要

### 用戶故事 C-2

**基於給定的資料做評測**

給定原始資料集與對應的隱私強化資料集到評估模組中，該流程會產生一份涵蓋預設/一般指標的隱私風險與效用的報告。

這裡「自訂資料」的概念是，使用者已經擁有合成資料，您只需要使用 `PETsARD` 做評測，不用跑整套 `PETsARD` 合成資料的流程。此時請參考 C-1、C-2 的說明，依照不同的 `Evaluator`，來對不同模組使用 `'custom_data'` 的設定：

#### 用戶故事 C-2a

C-2a 展示的是 `Evaluator` 使用「原始資料」對照「合成資料」進行比較的評測方式，例如 `method = 'default'` 或 `'sdmetrics-'` 開頭的 SDMetrics 評測工具。

「原始資料」可以直接用 `Loader` 讀入，此時「合成資料」需要放到 `Synthesizer` 當中、使用 `method = 'custom_data'` 來指定自訂資料，

當使用 `method = 'custom_data'` 之後，跟 `Loader` 一樣，使用 `filepath` 指定檔案位置。

#### 用戶故事 C-2b

C-2b 展示的是 `Evaluator` 使用「參與合成的原始資料」(original data, 縮寫為 ori)、「不參與合成的原始資料」(control data, 縮寫為 control)、與「合成資料」(synthesized data, 縮寫為 syn) 三者一起進行比較的合成方式，例如 `method = 'anonymeter-'` 開頭的 Anonymeter 評測工具。

「參與合成」跟「不參與合成」是利用了 `Splitter` 模組進行切割，所以請對 Splitter 使用 `method = 'custom_data'`，此時 `filepath` 需要兩個輸入，`'ori'` 對應了「參與合成的原始資料」，`'control'` 對應了「不參與合成的原始資料」。「合成資料」在 `Synthesizer` 的設定方法與 C-2a 一樣，

這裡我們特意同時展現了 `method = 'default'` 的評測。針對直接比對「原始資料」與「合成資料」的 C-2a 情境，C-2b 會自動地將 `Splitter` 當中的 `'ori'` 視作「原始資料」來比對，同時得到 SDMetrics 跟 Anonymeter 的結果。使用者應自行評估自己的資料切分方式，是否具有足夠的原始資料代表性。

## 用戶故事 D

**基於基準資料集做研究**

本示範將展示如何使用 `PETsARD` 的基準資料集來評估合成演算法。

在這個示範中，您作為進階的使用者，對於不同的差分隱私/合成資料技術、以及對應的評測指標有初步理解，希望評估技術彼此之間的差異等學術與實務議題。

而 `PETsARD` 將提供你完整的平台，藉由預先整合好的，在學術、比賽或實務上常用的基準資料集， `PETsARD` 能輕鬆設定不同基準資料集、執行在不同合成演算法上、並執行不同評測的實驗組合，讓您能輕鬆獲得綜合性資料的支持，專注在您的學術或開發工作上。

### 用戶故事 D-1

**於預設資料做合成**

指定資料合成演算法後，預設的經典資料集會用作輸入，並且該流程將使用該演算法輸出對應的隱私強化資料集。

### 用戶故事 D-2

**於多個資料做合成**

根據用戶故事 D-1，使用者可以改為指定一個資料集列表。

### 用戶故事 D-3

**於預設資料做合成與評測**

根據用戶故事 D-1，如果使用者啟用評估步驟，評估模組將會產生一份涵蓋所有資料集的隱私風險與效用指標報告。
