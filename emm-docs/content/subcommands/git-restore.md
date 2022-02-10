---
weight: 12 
---
### Restoring files in git

The `git-restore` subcommand will restore files from the staging area of all modules. The command will
attempt to restore files matching the given filespec in each module and display a list of modules
in which files were restore.

```bash
$ evg-module-manager git-restore --staged "."
Files restored from enterprise.
Files restored from base.
```
