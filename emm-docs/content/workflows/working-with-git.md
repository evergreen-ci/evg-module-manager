---
weight: 2
---
Once you have your [project setup]({{< relref "project-setup.md" >}}) with any enabled modules 
you want to work with, next you will want to create a branch to work on.

## Creating a branch to work on

You may want to run pull to get the latest changes for your base repository in additional to pulling
the latest changes, each enabled module will be checked out to the commit that was run with the 
latest commit in the base repo in evergreen.

```bash
$ evg-module-manager git-branch-pull
Base: pulled to latest
- enterprise: 07c4792479f85fb8af129a87ee6e116c4b7d7808
```

You can use the `git-branch-create` subcommand to create a local branch across all the repositories:
```bash
$ evg-module-manager git-branch-create --branch dbradf/my-test-branch
Branch 'dbradf/my-test-branch' created on:
 - enterprise
 - base
```

After your branch has been created, you can work on the branch and make whatever changes you wish.
Once you are ready to make a commit, the following subcommand will help you.

## Committing changes to git

First, you can see the status of all the modules with the `git-status` subcommand:

```bash
$ evg-module-manager git-status
Status of enterprise:
  On branch dbradf/my-test-branch
  Changes not staged for commit:
    (use "git add <file>..." to update what will be committed)
    (use "git restore <file>..." to discard changes in working directory)
        modified:   README

  no changes added to commit (use "git add" and/or "git commit -a")

Status of base:
  On branch dbradf/my-test-branch
  Changes not staged for commit:
    (use "git add <file>..." to update what will be committed)
    (use "git restore <file>..." to discard changes in working directory)
        modified:   README.md

  no changes added to commit (use "git add" and/or "git commit -a")
```

Once you have checked that the changes look as expected, you can add any changes you wish to
the staging area with the `git-add` subcommand. Note that the add will be run against all 
modules.  If you want to only add changes to a specific module, you will need to do that with 
manually git commands.

```bash
$ evg-module-manager git-add .
Files added to enterprise.
Files added to base.
```

If we run the `git-status` subcommand again, we can see that the changes are now staged to be
committed:

```bash
$ evg-module-manager git-status
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

After your changes have been staged, you can use the `git-commit` subcommand to create a new
commit. 
{{< hint info >}}
**NOTE**\
You can skip manually adding files by passing the `--add` flag to the `git-commit` 
subcommand, this will use the same behavior as you get from `git commit -a`.
{{< /hint >}}

```bash
$ evg-module-manager git-commit --message "My commit message"
Commit created in the following modules:
 - enterprise
 - base
```

Now your changes should be committed.

## What's next

Now that your changes have your changes ready, you can 
[send them to evergreen]({{< relref "working-with-evergreen.md" >}}).
