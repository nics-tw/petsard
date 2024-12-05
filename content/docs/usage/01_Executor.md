---
title: "Executor"
# description: "Guides lead a user through a specific task they want to accomplish, often with a sequence of steps."
# summary: ""
date: 2023-09-07T16:04:48+02:00
lastmod: 2023-09-07T16:04:48+02:00
draft: false
weight: 12
toc: true
---

The `Executor` interface is responsible for orchestrating and executing experiments. Ideally, once equipped with a `yaml` formatted experiment design file, it becomes the sole component you need to interact with.

```Python
from PETsARD import Executor

filename = 'Exec_Design.yaml'
exec = Executor(config=filename)
exec.run()
```

# `Executor`

The basic usage of `Executor` is providing the path of the experiment design file in `yaml` format for initialisation. See [YAML page](https://nics-tw.github.io/PETsARD/YAML.html) to know the format and content of the `YAML` file.

```Python
exec = Executor(config)
```

**Parameters**

`config` (`str`): The fullpath of the experiment design file.

## `run()`

Execute the experiments.
