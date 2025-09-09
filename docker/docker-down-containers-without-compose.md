# 在没有 compose 文件的情况下 down 容器

有时候机器重启后，我们会发现有一些容器被意外启动，这些容器可能是之前通过 `docker compose up` 起来的，但是后来我们删了 compose 文件。此时我们就不能通过 `docker compose down` 来停掉容器了，但我们又不想让这些容器在下次机器重启的时候启动。

此时我们可以这样做：

1. 检查容器的重启策略：`docker inspect` 里存储了容器的基本信息，里面包含当前的重启策略，你可以直接搜索 `Restart` 查找，也可以结合 `jq` 来直接获取相关字段：

    ```
    $ docker inspect f05fc1ea209a | jq '.[0].HostConfig.RestartPolicy'
    {
      "Name": "always",
      "MaximumRetryCount": 0
    }
    ```
  可以看到目前的重启策略是 `always`，即容器会一直重启，除非你 down 掉。
2. 更新容器的重启策略：`docker update --restart=no f05fc1ea209a`。
3. 删除或停止容器：`docker rm/stop f05fc1ea209a`。

这样容器就不会在下次开机时重启了。

PS：写完后突然发现，既然 `always` 策略生效的前提是容器存在，那直接删除容器不就行了？不用这么费劲了。but whatever，折腾一番学到了 `jq`，对 `inspect` 的结果也有了更多的认识。
