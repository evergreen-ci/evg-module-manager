---
weight: 4
---
Use the `git-branch-show` subcommand to see the local branch in the base repo and all modules. 
The currently checked out branch in each module will be preceded by an `*`.

```bash
$ evg-module-manager git-branch-show
Branches in 'enterprise':
  dbradf/my-test-branch
* master
Branches in 'base':
  dbradf/my-test-branch
* master
```
