---
weight: 1
---
To enable a modules in your local repo, use the `enable` command. If the module code is not
available locally, it will be cloned into the directory specified by the `modules-dir` option.
Modules are enabled by adding a symlink to the cloned repository at the modules "prefix".

```bash
$ evg-module-manager enable --module wiredtiger
```
