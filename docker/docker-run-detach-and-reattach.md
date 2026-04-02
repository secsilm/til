# 如何让 Docker 容器后台运行并随时进入

有时候我们想启动一个容器，跑一些程序，然后放到后台运行，我们先暂时退出这个容器。我们有两种方法实现。

## 方法 1：`sleep infinity`

这种方法会让容器陷入无限循环，开启后可通过 `docker exec` 进入。注意不可通过 `docker attach` 进入，这样进入只会和 `-it` 一样，进入了那个无限循环。

具体命令：

```bash
# 开启容器
docker run -d your_image sleep infinity

# 进入
docker exec -it container_id bash
```

## 方法 2：`Ctrl P` + `Ctrl Q`

这种方法比较接近日常用法，后续我应该都会使用这个方法。先用 `-it` 进入，然后通过 exec 进入。注意最好不要通过 attach 进入，因为这样的话，一旦你 ctrl d 退出了，那么这个容器也就退出了，因为 attach 的是容器内 pid=1 的主进程（来自 claude opus 4.6 extended thinking，未做核查）。而 exec 每次是新开一个 session，所以 ctrl d 也无妨。

具体命令：

```bash
# 开启容器
docker run -it your_image bash

# 退出
Ctrl P + Ctrl Q，mac 也一样

# 进入
docker exec -it container_id bash
```
