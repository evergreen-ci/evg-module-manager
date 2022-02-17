---
weight: 6
---
Use `git branch-delete` subcommand to delete an existing branch in all modules. Use the
`--branch` option to specify the name of the branch to delete.

The command will display the branch that was deleted along with all the modules the branch
was created on.

```bash
$ evg-module-manager git branch-delete --branch dbradf/my-test-branch
Branch 'dbradf/my-test-branch' delete from:
 - enterprise
 - base
```
