---
weight: 6
---
### Creating github pull request

{{< hint warning >}}
**Note**\
In order to create pull requests in github, you need to sure the `gh` command line tool
is available and authentication to github is configured. See 
[Github authentication](/getting-started/installation#github-authentication)
for details.
{{< /hint >}}

The `pull-request` subcommand will create pull requests across the base repo and all enabled 
modules.  

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
