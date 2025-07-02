---
title: Logging Configuration
type: docs
weight: 86
prev: docs/developer-guide/mpuccs
next: docs/developer-guide/experiment-name-in-reporter
---

## Logging Configuration

The logging configuration is specified in the `Executor` section of your YAML configuration file.

Click the below button to run this example in Colab:

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/nics-tw/petsard/blob/main/demo/developer-guide/logging-configuration.ipynb)

```yaml
---
Executor:
  log_output_type: both # Where to send logs: stdout, file, or both. Default is file
  log_level: DEBUG      # Log verbosity: DEBUG, INFO, WARNING, ERROR, CRITICAL. Default is INFO
  log_dir: demo_logs    # Directory for log files (auto-created if it doesn't exist). Default is ., means working directory
  log_filename: PETsARD_demo_{timestamp}.log # # Log file name template. Default is "PETsARD_{timestamp}.log"
# ... the rest is omitted
...
```

All four parameters are optional and can be used as needed. Additionally, the position of the `Executor` section in the YAML file does not affect its functionality.

### Output Destinations (log_output_type)

- `stdout`: Logs are printed to the console
- `file`: Logs are written to a file
- `both`: Logs are both printed to the console and written to a file

### Log File Naming (log_filename)

The `{timestamp}` placeholder in the filename will be replaced with the current date and time. You can omit it if you don't want a date in the filename.
