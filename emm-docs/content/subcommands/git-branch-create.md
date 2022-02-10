---
weight: 5
---
Use `git-branch-create` subcommand to create a new branch on the base repo and any enabled modules. Use the
`--branch` option to specify the name of the branch to create.

To create a branch named `my-branch`, use the following:
```bash
$ evg-module-manager git-branch-create --branch my-branch
```

By default, the branch will be created based on the currently checked out commit. You can use the
`--revision` option to base the commit off a different revision.

The command will display the branch that was created along with all the modules the branch
was created on.

```bash
$ evg-module-manager create-branch --branch my-branch --revision "revision_to_checkout"
Branch 'dbradf/my-test-branch' created on:
 - enterprise
 - base
```
