---
weight: 2
---
## Defining your evergreen project and module repository location

{{< hint info >}}
**Note**\
`evg-module-manager` expects to be run from the base directory of the repository for the
evergreen project you are working with.
{{< /hint >}}

Most actions need to know 2 pieces of information: what evergreen project is being used and where
to store module repos. There can be provided via command line options or via environment variables.

By default, modules will be stored in the parent directory (`..`) from where you are running the command
and the '`mongodb-mongo-master`' project will be used.

To override the defaults via command line options, use the `--evg-project` and `--modules-dir` flags:

```bash
$ evg-module-manager --evg-project mongodb-mongo-v5.0 --modules-dir ~/my_modules ...
```

To override the defaults via environment variables, use `EMM_EVG_PROJECT` and `EMM_MODULES_DIR`.

```bash
$ EMM_EVG_PROJECT=mongodb-mongo-v5.0 EMM_MODULES_DIR=~/mymodules evg-module-manager ...
```
