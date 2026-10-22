# 为不同项目的 Notebook 自动设置工作目录

我在工作中所使用的 Python 项目文件组织结构一直在变化，随着新知识和经验的加入，总会有不同的认知。到目前为止，我的默认组织结构如下：

```
├── config.py            // 配置文件，包含 redis、es 等数据库配置类，也用来加载 env。
├── data                 // 放相关的数据文件
├── data_types.py        // 数据类型定义，一般为 Pydantic model
├── deploy.sh            // format、build、push
├── docker-compose.yml   // compose 文件，里面包含一个示例
├── Dockerfile
├── format.sh            // 格式化代码
├── main.py.             // 主程序，如为 api 服务，则应命名为 app.py
├── log_config.py        // logging 配置，使用 loguru
├── pyproject.toml       // ruff、pytest 等配置
├── README.md
├── requirements.txt
├── start.sh             // 启动脚本
├── tests                // pytest 测试文件目录，此部分一般由 ai 完成
└── utils.py             // 共用 helper
```

所有文件均放在项目的根目录，典型的 flat 形式（而不是 `src/` 形式）。我写的程序一般是一次性脚本、长时间运行的程序（例如队列消费）或者 api（例如 fastapi app）。我基本都按照这种结构进行处理，我也尝试过 `src/` 形式，但是带来了不少麻烦。

除此之外，经常还会有 notebook 文件，尤其是模型开发和数据分析工作。这些文件我以前都是直接放在根目录下，因为我发现这样 import 现有模块（比如 utils）最为方便，尽管数量多的时候看起来有点乱。我也尝试过将这些文件统一放在 `notebooks/` 目录中，但是我发现这样会带来 import 问题：

1. 你不能直接 `import utils`，因为该模块处于父级目录中，你不得不每次都写 `sys.path.insert`，一点都不优雅。
2. 你写了 insert 后，utils 可以导入了，但是如果 utils 里的函数读取了 `data/` 下的文件，那么这就会导致失败。

今天看了 real python 的 [Python Project Structure: How to Choose the Right Layout](https://realpython.com/python-application-layouts/)，借此机会，和 ChatGPT 再次讨论这一问题。经过[几轮的 back and forth](https://chatgpt.com/share/6ad06d37-fc48-83ea-9ada-3d74b56ffd68)，最终得到下面的解决方案，只需一次改动，无需在每次新建 notebook 时手动写代码：

在 Jupyter Server 的配置文件 `~/.jupyter/jupyter_server_config.py` 中添加：

```python
from pathlib import PurePosixPath

from jupyter_server.services.contents.filemanager import FileContentsManager


class ProjectContentsManager(AsyncLargeFileManager):
    async def get_kernel_path(self, path, model=None):
        parts = PurePosixPath(path).parts

        if path.endswith(".ipynb") and "notebooks" in parts[:-1]:
            index = parts.index("notebooks")
            kernel_path = "/".join(parts[:index])
            self.log.info("Kernel CWD: %s -> %s", path, kernel_path)
            return kernel_path

        return await super().get_kernel_path(path, model)

c.ServerApp.contents_manager_class = ProjectContentsManager
```

这样每次遇到 `notebooks/` 中的文件，都会自动将 cwd 改为 `notebooks/` 所在目录，即使 `notebooks/` 中有多层目录也没问题，而且不影响不在 `notebooks/` 中的文件。唯一的要求就是在根目录创建 `notebooks/`，然后将所有的 nb 都放在这里。

需要注意的是，如果你打开一个旧的 nb，会自动复用旧的 kernel，即使你 restart 或者 shutdown kernel。此时你需要点击右上角的 kernel，手动选择到你想要的 kernel 即可，此时才会执行 `start_kernel_for_session()`，而上面我们定义的 `get_kernel_path()` 就是在这个函数中执行的。

完美！
