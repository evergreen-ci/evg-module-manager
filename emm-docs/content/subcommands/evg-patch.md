---
weight: 14 
---
### Creating an Evergreen patch build

{{< hint warning >}}
**Note**\
In order to create a patch build in Evergreen, you need to ensure the `evergreen` 
command line tool is available and configured. See [Evergreen authentication](/getting-started/installation#evergreen-authentication)
for details.
{{< /hint >}}

The `evg-patch` subcommand will create an evergreen patch build with changes to your base repository 
and any modules that are currently enabled. You can pass along any options that the 
`evergreen patch` command supports, however, the `--skip_confirm` and `--project` options are 
already specified by the tools and should not be included.

```bash
$ evg-module-manager evg-patch -d "my patch description" -u
```
