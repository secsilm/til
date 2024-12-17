# git clone 的 depth 与 commit 时间

我们可以使用如下命令来获取一个文件的 commit 时间：

```bash
$ git log -1 --format=%cd --date=iso -- {filepath}
2024-12-17 14:53:34 +0800
```

然而如果你 git clone 时指定了 `--depth=1`，即只拉取最新的 commit，那么此时所有文件的 commit 时间都会是仓库的更新时间。

这种情况也发生在你在 GitHub actions 里执行拉取时，所以在你的 yml 文件里拉取仓库的位置，加入如下 `with` 代码：

```yaml
- name: Checkout code
  uses: actions/checkout@v3  # Check out the repository code
  with:
    fetch-depth: 0  # Fetch the full Git history
```
