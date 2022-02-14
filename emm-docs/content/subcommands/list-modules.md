---
weight: 0
---
To see what modules are available for the current project, use the `list-modules` command:

```bash
$ evg-modules-manager --evg-project sys-perf list-modules
- enterprise
- wtdevelop
```

You can use the `--show-details` option to get more details about each module.

```bash
$ evg-module-manager --evg-project mongodb-mongo-master list-modules --show-details
- enterprise
        prefix: src/mongo/db/modules
        repo: git@github.com:10gen/mongo-enterprise-modules.git
        branch: master
- wtdevelop
        prefix: src/third_party
        repo: git@github.com:wiredtiger/wiredtiger.git
        branch: develop
```
You can also pass the `--enabled` option to only list modules which are currently active in your
local repository.

```bash
$ evg-module-manager --evg-project mongodb-mongo-master list-modules --enabled
- wtdevelop
```
