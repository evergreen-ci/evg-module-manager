---
weight: 9
---
Use `git-branch-pull` subcommand to get the latest changes for your base repo and sync all 
modules to the latest commit of the base repo.

{{< hint warning >}}
**NOTE**
Since Evergreen builds are only run against a single branch. You will only want to run this
subcommand on on the branch tracked by Evergreen. 
{{< /hint >}}

The command will display the revision that each module to set to.

```bash
$ evg-module-manager git-branch-pull
Base: pulled to latest
- enterprise: 07c4792479f85fb8af129a87ee6e116c4b7d7808
```
