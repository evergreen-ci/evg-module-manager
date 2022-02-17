---
weight: 5
---
Once you have your changes ready to share with others you can use evg-module-manager to create
a Github Pull Request.

## Creating a Pull Request

The `pull-request` subcommand will create pull requests for the base repo and all modules that
contain changes. If more than 1 pull request is created, a comment will be added to each pull
request with links to the others.

{{< hint info>}}
**NOTE**\
By default the `pull-request` subcommand with use information from the git commits to determine
the pull request title and body. If you would prefer, you can use the `--title` and `--body` options
to specify the title and body yourself.
{{< /hint >}}

```bash
$ evg-module-manager pull-request
```

## What's next

Now that your changes have been reviewed, you can 
[send them to evergreen]({{< relref "working-with-evergreen.md" >}}).
