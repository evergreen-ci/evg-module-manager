---
weight: 13
---
Use the `git-commit` subcommand to create a new commit with your changes. The commit will be
created on all modules that contain committable changes. By default, this means changes that have
been staged. You can use the `--add` flag to automatically include any changes to tracked files as
part of the commit.

If you are creating a new commit, use the `--message` option to supply a commit message. If you 
would like to commit the changes to the previous commit, use the `--amend` flag instead.

Creating a new commit:

```bash
$ evg-module-manager git-commit --message "My commit message"
Commit created in the following modules:
 - enterprise
 - base
```

Amending to a previous commit:

```bash
$ evg-module-manager git-commit --amend
Commit created in the following modules:
 - enterprise
 - base
```
