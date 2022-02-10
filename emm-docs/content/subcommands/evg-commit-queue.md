---
weight: 15
---
## Submitting to the commit-queue

{{< hint warning >}}
**Note**\
In order to submit changes to the commit queue in Evergreen, you need to ensure the 
`evergreen` command line tool is available and configured. See 
[Evergreen authentication](/getting-started/installation#evergreen-authentication) for details.
{{< /hint >}}

The `evg-commit-queue` subcommand will submit changes to the evergreen commit-queue that include 
changes to your base repository and any modules that are currently enabled. You can pass along any
options that the `evergreen commit-queue merge` command supports, however, the `--skip_confirm` 
and `--project` options are already specified by the tools and should not be included.

```bash
$ evg-module-manager evg-commit-queue
```
