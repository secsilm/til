# uv 安装私有 devpi 上的 package

devpi 是一个可自部署的 package index server，我在部门内部部署了一个以方便安装和维护内部包。在需要安装的时候，可以使用如下 pip 命令安装：

```
pip install my_internal_package --extra-index-url http://{ip}:{port}/root/{project} --trusted-host {ip}
```

但是在使用 uv 时，如果直接将 `pip install` 替换为 `uv add` 时，会报错：

```
warning: Indexes specified via `--extra-index-url` will not be persisted to the `pyproject.toml` file; use `--index` instead.
  × No solution found when resolving dependencies:
  ╰─▶ Because there are no versions of localnews and your project depends on localnews, we can conclude that your project's requirements are unsatisfiable.
  help: If you want to add the package regardless of the failed resolution, provide the `--frozen` flag to skip locking and syncing.
```

根据我对 https://github.com/astral-sh/uv/issues/4907 和 https://github.com/astral-sh/uv/issues/4907#issuecomment-2299793116 的粗浅理解，这是由于默认的 index url 不是一个 simple index，而 uv 目前仅支持 simple index，所以我们需要给其提供 simple index，即在后面加上 `/+simple`：

```
uv add my_package --extra-index-url http://{ip}:{port}/root/{project}/+simple --trusted-host {ip}
```

但是根据上面的 warning，这个 index url 是不会写入 `pyproject.toml` 的，需要换成 `--index`，这样 `pyproject.toml` 就会包含这个 index url 了：

```toml
[project]
name = "test-uv-devpi"
version = "0.1.0"
requires-python = ">=3.11"
dependencies = [
    "my_package>=0.0.17",
]

[[tool.uv.index]]
url = "http://{ip}:{port}/root/{project}/+simple"
```
