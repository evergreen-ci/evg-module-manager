---
weight: 3
---
Use `create-branch` command to create a new branch on the base repo and any enabled modules. Use the
`--branch` option to specify the name of the branch to create.

To create a branch named `my-branch`, use the following:
```bash
$ evg-module-manager create-branch --branch my-branch
```

By default, the branch will be created based on the currently checked out commit. You can use the
`--revision` option to base the commit off a different revision.

To create a branch with the revision you want to start work with:
```bash
$ evg-module-manager create-branch --branch my-branch --revision "revision_to_checkout"
```
