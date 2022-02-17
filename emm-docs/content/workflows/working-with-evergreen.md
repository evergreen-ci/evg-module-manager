---
weight: 4
---
At some point, you will want to test your changes in Evergreen. You can use evg-module-manager
to gather up changes to all your enabled modules and send them together.

## Creating Patch Builds

The `evg patch` subcommand will create a patch build with changes from your base repository and
all enabled repositories.

{{< hint info >}}
**Note**\
You can pass any options supported by the `evergreen patch` tool to the `evg-patch` subcommand.
See the [evergreen docs](https://github.com/evergreen-ci/evergreen/wiki/Using-the-Command-Line-Tool#basic-patch-usage)
for more information
{{< /hint >}}

```bash
$ evg-module-manager evg patch -d "description of my patch"
Patch Submitted: https://evergreen.mongodb.com/patch/620aba4f3627e05537c2f52e?redirect_spruce_users=true
```

## Submitting changes to the commit-queue

Once you are ready to merge you changes, you can send them all to the commit-queue with the
`evg commit-queue` subcommand.

{{< hint info >}}
**Note**\
You can pass any options supported by the `evergreen commit-queue merge` tool to the `evg-commit-queue` subcommand.
See the [evergreen docs](https://github.com/evergreen-ci/evergreen/wiki/Commit-Queue#cli)
for more information
{{< /hint >}}

```bash
$ evg-module-manager evg commit-queue
```

## What's next

Now that your changes have been sent to evergreen, you can 
[create a pull request]({{< relref "creating-pull-requests.md" >}}) or 
[clean up your finished branch]({{< relref "cleaning-up.md" >}}).
