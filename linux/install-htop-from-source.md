# 源码编译安装 htop

[htop](https://htop.dev/index.html) 是一个很好用的交互式进程查看器。我们可以使用 `sudo apt install htop` 来安装。但是有时候不知道怎么回事一直安装不到最新版，比如我的就一直停留在 2.2.0，然后最新版已经 3.3.0 了。

这时我们可以直接源码编译安装，详细的各个平台的安装可以参考[官方 GitHub](https://github.com/htop-dev/htop)。这里我简单记录下在 Ubuntu 22.04 下的安装：

```bash
# 1. 安装依赖
sudo apt install libncursesw5-dev autotools-dev autoconf automake build-essential

# 2. 编译
./autogen.sh && ./configure && make

# 3. 安装
sudo make install
```

注意这里默认安装到 `/usr/local/bin`，而 apt 安装的一般在 `/usr/bin`。

编译安装后执行 `htop` 时，如果发现命令找不到，那么将 `export PATH="/usr/local/bin:$PATH"` 添加到 `~/.bashrc` 的底部，然后执行 `source ~/.bashrc` 即可。
