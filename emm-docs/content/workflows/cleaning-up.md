---
weight: 10
---
Once your branch has been [merged via the commit-queue]({{< relref "working-with-evergreen.md" >}}), 
you will likely want to cleanup it up.

## Switching to a selected branch

You cannot delete a branch you currently have checked out, so the first step to cleaning up 
the branch is to switch to a different branch. You can use the `git-branch-switch` subcommand
to change branches.

```bash
$ evg-module-manager git-branch-switch --branch master
Switched to 'master' in:
 - enterprise
 - base
```

## Deleting old branches

Once you no longer have the branch you wish to remove checked out, you can remove it. First, you can 
use the `git-branch-show` subcommand to see the existing branches in each enabled repository.

```bash
$ evg-module-manager git-branch-show
Branches in 'enterprise':
  dbradf/my-test-branch
* master
Branches in 'base':
  dbradf/my-test-branch
* master
```

Next, you can use the `git-branch-delete` subcommand to remove the desired branch.

```bash
$ evg-module-manager git-branch-delete --branch dbradf/my-test-branch
Branch 'dbradf/my-test-branch' delete from:
 - enterprise
 - base
```

If you run the `git-branch-show` subcommand again, you will see that the branch no longer shows
up.

```bash
$ evg-module-manager git-branch-show
Branches in 'enterprise':
* master
Branches in 'base':
* master
```

