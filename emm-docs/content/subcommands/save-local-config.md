---
weight: 17
---
The `save-local-config` subcommand will write a configuration file to the local directory that
future executions of `evg-module-manager` run from the same directory can use to determine the
configuration options to use.

```bash
$ evg-module-manager save-local-config --help
Usage: evg-module-manager save-local-config [OPTIONS]

  Save the given configuration options at './.emm-local.yml'.

  When this file is present in the directory `evg-module-manager` is run from, the values defined
  in the file will be used. This allows you to run `evg-module-manager` without needing to specify
  global options every run.

  The supported option are:
  * evg_project
  * modules_directory

Options:
  --help  Show this message and exit.

$ evg-module-manager --evg-project=evg-module-manager save-local-config
$ cat .emm-local.yml
evg_project: evg-module-manager
modules_directory: ..
```
