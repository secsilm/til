# 源码编译安装 htop

[htop](https://htop.dev/index.html) 是一个很好用的交互式进程查看器。我们可以使用 `sudo apt install htop` 来安装。但是有时候不知道怎么回事一直安装不到最新版，比如我的就一直停留在 2.2.0，然后最新版已经 3.3.0 了。

这时我们可以从[官方 release](https://github.com/htop-dev/htop/releases) 下载源码，然后直接源码编译安装，详细的各个平台的安装可以参考[官方 GitHub](https://github.com/htop-dev/htop)。这里我简单记录下在 Ubuntu 22.04 下的安装：

```bash
# 1. 下载最新版
wget https://github.com/htop-dev/htop/releases/download/3.3.0/htop-3.3.0.tar.xz

# 2. 解压
tar xf htop-3.3.0.tar.xz

# 3. 安装依赖
cd htop-3.3.0
sudo apt install libncursesw5-dev autotools-dev autoconf automake build-essential

# 4. 编译
./autogen.sh && ./configure && make

# 5. 安装
sudo make install
```

注意这里默认安装到 `/usr/local/bin`，而 apt 安装的一般在 `/usr/bin`。

编译安装后执行 `htop` 时，如果发现命令找不到，那么将 `export PATH="/usr/local/bin:$PATH"` 添加到 `~/.bashrc` 的底部，然后执行 `source ~/.bashrc` 即可。
