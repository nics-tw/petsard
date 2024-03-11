User Story demo is designed to assist users in setting their own configuration file. Enjoy : )

It is recommended to refer to the `demo/User Story...ipynb` user story scenarios in the [demo/REAMD.ME](https://github.com/nics-tw/PETsARD/tree/main/demo) and [yaml/README.md](https://github.com/nics-tw/PETsARD/tree/main/yaml), which helps clarify the implementation of your requirements.

用戶故事的示範旨在協助使用者設定您自身的設定檔案。祝您使用愉快 : )

建議搭配 GitHub 倉儲中 [demo/README.md](https://github.com/nics-tw/PETsARD/tree/main/demo) 的 `demo/User Story A/B/C/D.ipynb` 用戶故事情境範例、與 [yaml/README.md](https://github.com/nics-tw/PETsARD/tree/main/yaml)，幫助釐清您的需求如何實現。


## Environment

In `PETsARD`, the only thing you need to do is to prepare a YAML file following the example and execute the `Executor`.

Assuming your YAML file is `config.yaml`, your Python code would be:

在 `PETsARD` 中，您唯一所需要做的，便是參考範例準備 YAML 檔案，並執行 `Executor`。

假設您的 YAML 檔案名稱為 `config.yaml`，則您的 Python 程式碼為：


```Python
exec = Executor(config='config.yaml')
exec.run()
```

# User Story A
**Privacy Enhancing Data Generation**

This demo illustrates how to generate privacy-enhanced data using `PETsARD`.

In this demonstration, you, as the user, already possess a data file locally, and `PETsARD` will assist you in loading that file and then generating a privacy-enhanced version of it.

Besides, privacy-enhancing algorithms often have restrictions on specific formats and/or specific data processing procedures. `PETsARD` takes care of these as well. `PETsARD` offers both default and customizable preprocessing and postprocessing workflows to help users get started quickly.

本示範將展示如何使用 `PETsARD` 生成隱私強化資料。

在這個示範中，您作為使用者，在本機上已經擁有一份資料檔案，而 `PETsARD` 將幫助您讀取該檔案、然後生成經隱私強化後的版本。

同時，隱私強化演算法通常都有特定資料格式、以及特定資料處理程序的限制，`PETsARD` 已經為使用者考慮到這點，`PETsARD` 提供預設與可客製化的前後處理流程，幫助使用者快速上手。


## User Story A-1
**Default Synthesizing**

Given an original dataset without specifying any algorithm, the pipeline will generate a list of privacy-enhanced datasets using the default algorithms.

給定一個原始資料集、但未指定演算法，該流程會利用預設的演算法生成一組隱私強化資料集。


## User Story A-2
**Customized Synthesizing**

Given an original dataset, specified privacy enhancing data generation algorithms and parameters, the pipeline will generate a privacy-enhanced dataset.

給定一個原始資料集，並指定隱私強化技術生成演算法與參數，該流程會依此產生隱私強化資料集。


# User Story B
**Privacy Enhancing Data Generation and Evaluation**

This demo will show how to generate and evaluate privacy-enhanced data using `PETsARD`.

In this demonstration, you, as the user, already possess a data file locally, and `PETsARD` will assist you in loading that file and then generating a privacy-enhanced version of it.

本示範將展示如何使用 `PETsARD` 生成與評測隱私強化資料。

在這個示範中，您作為使用者，在本機上已經擁有一份資料檔案，而 `PETsARD` 將幫助您讀取該檔案、生成經隱私強化後的版本、最終評測。


## User Story B-1
**Default Evaluating**

Following User Story A, if users enable the "evaluate" step ,  the evaluation module will create a report covering default privacy risk and utility metrics.

根據用戶故事 A，如果使用者啟用了 "evaluate" 步驟，評估模組會產生涵蓋預設的隱私風險與效用指標的報告。


## User Story B-2
**Customized Evaluating**

Following User Story B-1, if specific types of metrics are set or a customized evaluation script is provided, the module will create a customized evaluation report.

根據用戶故事 B-1，如果指定特定的指標、或是提供用戶自定義的評估腳本，模組會產生客製化的評估報告。


# User Story C
**Privacy Enhancing Data Evaluation**


This demo will show how to evaluate privacy-enhanced data using `PETsARD`.

In this demonstration, you, as the user, already have a data file on your local machine, as well as its corresponding synthetic data results, which are likely from your existing privacy protection service. `PETsARD` will assist you in reading these files and evaluating the results, helping you compare your current solution with other technologies.

本示範將展示如何使用 `PETsARD` 生成與評測隱私強化資料。

在這個示範中，您作為使用者，在本機上已經擁有一份資料檔案、以及其對應的合成資料結果，這很可能是來自於您現有的隱私保護服務，而 `PETsARD` 將幫助您讀取這些檔案、評測結果，幫助您針對現有的解決方案跟其他技術做比較。


## User Story C-1
**Default Describing**

Given a dataset as an input, the pipeline can go through the "describe" module to get a summary of the dataset.

給定一個資料集做輸入，該流程可以藉由調用 "describe" 模組而得到該資料集的摘要


## User Story C-2
**Evaluating based on given data**

Given an original dataset and a privacy-enhanced dataset to the evaluation module, the pipeline will create a report covering default/general metrics of privacy risk and utility.

給定原始資料集與對應的隱私強化資料集到評估模組中，該流程會產生一份涵蓋預設/一般指標的隱私風險與效用的報告。

The concept of custom data is that, in the complete User Story B which involves "generating privacy-enhanced data" + "evaluating data", wherever the synthesized data or the partitioned data is generated in the process, that particular module is where `method = 'custom_data'` is applied.

自訂資料的概念是，原本完整的 User Story B 「生成隱私強化資料」+「評測資料」，這個流程當中，合成後的資料、切分後的資料會產生在流程的哪個模組，便對哪個模組使用 `method = 'custom_data'`。


### User Story C-2a

C-2a demonstrates the evaluation approach of the Evaluator as comparing "original data" with "synthetic data," for instance, using`method = 'default'` or tools starting with `'sdmetrics-'` from SDMetrics.

The "original data" can be directly loaded using the Loader. At this point, the "synthetic data" needs to be placed in the Synthesizer, using `method = 'custom_data'` to specify custom data.

After using `method = 'custom_data'`, similar to the Loader, the file location is specified using `filepath`.

C-2a 展示的是 Evaluator 的評測方式是「原始資料」對照「合成資料」，例如 `method = 'default'` 或 `'sdmetrics-'` 開頭的 SDMetrics 評測工具。

「原始資料」可以直接用 Loader 讀入，此時「合成資料」需要放到 Synthesizer 當中、使用 `method = 'custom_data'` 來指定自訂資料，

當使用 `method = 'custom_data'` 之後，跟 Loader 一樣，使用 `filepath` 指定檔案位置。


### User Story C-2b


C-2b demonstrates the evaluation method of the Evaluator as involving "original data used in synthesis" (abbreviated as ori), "original data not used in synthesis" (abbreviated as control), and "synthesized data" (abbreviated as syn), for example, using tools starting with `method ='anonymeter-'` from Anonymeter.

(Original data) "Participating in synthesis" and "not participating in synthesis" are achieved by using the Splitter module to divide the data. Therefore, please apply `method = 'custom_data'` to the Splitter, where `filepath` requires two inputs: `'ori'` corresponds to "original data used in synthesis," and `'control'` corresponds to "original data not used in synthesis." The setting method for "synthesized data" in the Synthesizer remains the same as C-2a.

Here, we specifically also demonstrate the evaluation with `method = 'default'`. For scenarios directly comparing "original data" and "synthesized data," C-2b automatically considers the `'ori'` in the Splitter as "original data" for comparison, obtaining results from both SDMetrics and Anonymeter. Users should evaluate their own data partitioning method to ensure it has sufficient representativeness of the original data.

C-2b 展示的是 Evaluator 的評測方式是「參與合成的原始資料」(original data, 縮寫為 ori)、「不參與合成的原始資料」(control data, 縮寫為 control)、與「合成資料」(synthesized data, 縮寫為 syn)，例如 `method ='anonymeter-'` 開頭的 Anonymeter 評測工具。

「參與合成」跟「不參與合成」是利用了 Splitter 模組進行切割，所以請對 Splitter 使用 `method = 'custom_data'`，此時 `filepath` 需要兩個輸入，`'ori'` 對應了「參與合成的原始資料」，`'control'` 對應了「不參與合成的原始資料」。「合成資料」在 Synthesizer 的設定方法與 C-2a 一樣，

這裡我們特意同時展現了 `method = 'default'` 的評測。針對直接比對「原始資料」與「合成資料」的 C-2a 情境，C-2b 會自動地將 Splitter 當中的 `'ori'` 視作「原始資料」來比對，同時得到 SDMetrics 跟 Anonymeter 的結果。使用者應自行評估自己的資料切分方式，是否具有足夠的原始資料代表性。


# User Story D
**Research on Benchmark datasets**

This demo will show how to use `PETsARD`'s benchmark datasets to evaluate synthetic algorithms.

In this demonstration, as an advanced user with a basic understanding of different differential privacy/synthetic data technologies and their corresponding evaluation metrics, you aim to assess the differences between technologies and other academic and practical issues.

PETsARD provides a complete platform that, by integrating commonly used benchmark datasets in academics, competitions, or practical applications, allows for easy setup of different benchmark datasets, execution on various synthetic algorithms, and execution of different evaluation combinations. This enables you to easily obtain comprehensive data support, focusing on your academic or development work.

本示範將展示如何使用 `PETsARD` 的基準資料集來評估合成演算法。

在這個示範中，您作為進階的使用者，對於不同的差分隱私/合成資料技術、以及對應的評測指標有初步理解，希望評估技術彼此之間的差異等學術與實務議題。

而 `PETsARD` 將提供你完整的平台，藉由預先整合好的，在學術、比賽或實務上常用的基準資料集， `PETsARD` 能輕鬆設定不同基準資料集、執行在不同合成演算法上、並執行不同評測的實驗組合，讓您能輕鬆獲得綜合性資料的支持，專注在您的學術或開發工作上。


## User Story D-1
**Synthesizing on default data**

With a specified data generation algorithm, a default benchmark dataset collection will serve as inputs, and the pipeline will generate the corresponding privacy-enhanced datasets as output, using the selected algorithm.

指定資料生成演算法後，預設的經典資料集會用作輸入，並且該流程將使用該演算法輸出對應的隱私強化資料集。


## User Story D-2
**Synthesizing on default data**

Following User Story D-1, the user can specify a list of datasets instead.

根據用戶故事 D-1，使用者可以改為指定一個資料集列表。


## User Story D-3
**Synthesizing and Evaluating on default data**

Following User Story D-1, if users enable the evaluation step, the evaluation module will create a report covering default privacy risk and utility metrics for all datasets.
根據用戶故事 D-1，如果使用者啟用評估步驟，評估模組將會產生一份涵蓋所有資料集的隱私風險與效用指標報告。
