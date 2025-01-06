---
title: PETsARD (/pəˈtɑrd/)
toc: false
---

<p style="text-align:center">
  Privacy Enhancing Technologies Analysis, Research, and Development
</p>

<p align="center"><img src="/petsard/images/PETsARD-logo.png"></p>

`PETsARD` (Privacy Enhancing Technologies Analysis, Research, and Development, /pəˈtɑrd/) is a Python library for facilitating data generation algorithm and their evaluation processes.

The main functionalities include dataset description, various dataset generation algorithms, and the measurements on privacy protection and utility.

- [Release Note](https://github.com/nics-tw/petsard/releases)
  - Release note provides information of each version of `PETsARD`.
- [CHANGELOG.md](https://github.com/nics-tw/petsard/blob/main/CHANGELOG.md)
  - Changelog provides evolution of the `PETsARD` over time.

## Explore

{{< cards >}}
{{< card link="docs/design-structure/" title="Docs" icon="book-open" >}}
{{< card link="about" title="About" icon="user" >}}
{{< /cards >}}

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change. And please make sure to update tests as appropriate.

## License

This project is licensed under `MIT` License with additional restrictions due to dependencies. The most significant restriction comes from SDV's Business Source License 1.1, which prohibits using this software as a commercial synthetic data service. For detailed licensing information, please see the LICENSE file.

Key Dependencies' Licenses:

- SDV: Business Source License 1.1
- Anonymeter: The Clear BSD License
- SDMetrics: MIT License
- Smartnoise: MIT License

For commercial use involving synthetic data services, please contact DataCebo, Inc.

## Citation

- `Synthesizer` module:
  - SDV - [sdv-dev/SDV](https://github.com/sdv-dev/SDV):
    - Patki, N., Wedge, R., & Veeramachaneni, K. (2016). The Synthetic Data Vault. IEEE International Conference on Data Science and Advanced Analytics (DSAA), 399–410. https://doi.org/10.1109/DSAA.2016.49
  - smartnoise - [opendp/smartnoise-sdk](https://github.com/opendp/smartnoise-sdk):
- `Evaluator` module:
  - Anonymeter - [statice/anonymeter](https://github.com/statice/anonymeter):
    - Giomi, M., Boenisch, F., Wehmeyer, C., & Tasnádi, B. (2023). A Unified Framework for Quantifying Privacy Risk in Synthetic Data. Proceedings of Privacy Enhancing Technologies Symposium. https://doi.org/10.56553/popets-2023-0055
  - SDMetrics - [sdv-dev/SDMetrics](https://github.com/sdv-dev/SDMetrics)
