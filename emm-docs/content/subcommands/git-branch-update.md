---
weight: 8
---
Use the `git branch-update` subcommand to update your current branch with the changes made remotely. 

The `git branch-update` subcommand will: 
* fetch the latest changes from the origin of all the repositories.
* update your branch with the latest changes in the base repository.
* update all enabled modules up to the change associated with where the base repository was updated to.

```bash
$ evg-module-manager git branch-update
Base: updated to latest 'master'
- enterprise: 07c4792479f85fb8af129a87ee6e116c4b7d7808
```
