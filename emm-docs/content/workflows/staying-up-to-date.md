---
weight: 3
---
After you have been working on a branch for some time, you will likely want to update your branch
with the latest changes from the branch it was based on. 

## Updating your branch

The `git branch-update` subcommand will: 
* fetch the latest changes from the origin of all the repositories.
* update your branch with the latest changes in the base repository.
* update all enabled modules up to the change associated with where the base repository was updated to.

```bash
$ evg-module-manager git branch-update
Base: updated to latest 'master'
- enterprise: 07c4792479f85fb8af129a87ee6e116c4b7d7808
```

## What's next

Now that your changes have been updated, you can 
[create a pull request]({{< relref "creating-pull-requests.md" >}}) or 
[send them to evergreen]({{< relref "working-with-evergreen.md" >}}).
