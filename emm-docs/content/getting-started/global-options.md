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
to store module repos. These can be provided via command line options or via environment variables.

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

## Remembering configuration

When working in a repository, it would be useful if `evg-module-manager` could remember which
evergreen project was associated with the repository so that you don't have to specify it 
every run. You can use a local configuration file to do this.

A local configuration file is a file that lives in the directory that you are running 
`evg-module-manager` from and provides configuration options. 

The file should be name `.emm-local.yml` and be in the yaml file format. `evg-module-manager` 
can automatically create the file for you with the `save-local-config` subcommand:

```bash
$ evg-module-manager --evg-project=evg-module-manager save-local-config
$ cat .emm-local.yml
evg_project: evg-module-manager
modules_directory: ..
```

Any time the `evg-module-manager` is run in a directory with a `.emm-local.yml` file, the values
in that files will be used for configuration.
