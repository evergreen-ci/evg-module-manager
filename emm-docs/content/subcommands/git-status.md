---
weight: 10 
---
The `git status` subcommand will display the current status of the base repository and the 
repository of all modules.

```bash
$ evg-module-manager git status
Status of enterprise:
  On branch dbradf/my-test-branch
  Changes to be committed:
    (use "git restore --staged <file>..." to unstage)
        modified:   README

Status of base:
  On branch dbradf/my-test-branch
  Changes to be committed:
    (use "git restore --staged <file>..." to unstage)
        modified:   README.md
```
