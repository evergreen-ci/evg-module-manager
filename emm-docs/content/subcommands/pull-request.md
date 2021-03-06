---
weight: 16
---
### Creating github pull request

{{< hint warning >}}
**Note**\
In order to create pull requests in github, you need to sure the `gh` command line tool
is available and authentication to github is configured. See
[Github authentication]({{< ref "/getting-started/installation#github-authentication" >}})
for details.
{{< /hint >}}

The `pull-request` subcommand will create pull requests across the base repo and all enabled
modules.


{{< hint warning >}}
**Note**\
This command will create a pull request against the `origin` repository in github.
You can run `git remote show origin` to confirm this is the repository you would like to use.

```bash
$ git remote show origin
* remote origin
  Fetch URL: git@github.com:mongodb/mongo.git
  Push  URL: git@github.com:mongodb/mongo.git
  HEAD branch: master
  Remote branches:
...
```

You can change the `origin` repository with the `git remote set-url origin <new_remote_url>` command.
{{< /hint >}}

After local changes have been committed in all repos, you can create the pull request from the base
repo, and all enabled modules with changes will create a separate pull request. Each pull
request will have comments that contain links for all other modules' pull requests.

To create pull requests in base repo and all enabled modules:

```bash
$ evg-module-manager pull-request
```

By default, the pull request title and body will be determined based on the commits. To override
these, the `--title` and `--body` options can be specified. If you provide the `--body` option,
you must also provide a `--title`.

```bash
$ evg-module-manager pull-request --title "my pull request title" --body "my pull request body"
```
