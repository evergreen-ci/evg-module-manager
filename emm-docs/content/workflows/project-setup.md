---
weight: 1
---
When you first start work on a change, you will want to enable any modules that you will be 
working with.

You can see what modules are available with the `list-modules` subcommand:

```bash
$ evg-module-manager list-modules
- enterprise
- wtdevelop
```

Then you can enable any modules you wish with the `enable` subcommand:

```bash
$ evg-module-manager enable -m enterprise
```

{{< hint info >}}
**Note**\
Enabling a module will attempt to checkout the module's repository to the commit
that was associated with the base commit in Evergreen.
{{< /hint >}}

Finally, you can verify that the module is active with the `list-modules --enabled` subcommand:

```bash
$ evg-module-manager list-modules --enabled
- enterprise
```


## What's Next

Once all the modules you are working with have been enabled, you are ready to start 
[making changes]({{< relref "working-with-git.md" >}}).
