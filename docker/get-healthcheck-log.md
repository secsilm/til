# 获取 docker 健康检查的日志

docker 有一个特性是可以检查容器是否健康，每隔一定时间进行拨测。以在 docker compose 中的配置为例：

```yml
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:8016"]
  interval: 30s
  timeout: 10s
  retries: 10
  start_period: 60s
```

就表示容器启动 `start_period=60s` 后，每隔 `interval=30s` 执行一次 `test` 的命令，即 `curl -f http://localhost:8016`，超时设置为 `timeout=10s`，最大重试次数为 `retries=10`。如果最后 `test` 命令还是没成功，那么就标识为 `unhealthy`，否则为 `healthy`。

注意 `test` 命令是在**容器内**执行的。

但是有时候容器正常启动了，却仍然标识为 `unhealthy`。此时我们就想知道，`test` 命令的具体输出是什么。那么我们可以使用以下命令：

```bash
docker inspect <container_id> --format='{{json .State.Health}}' | python -m json.tool
```

将 `<container_id>` 替换为你的容器 id 即可。样例输出如下：

```json
{
    "Status": "unhealthy",
    "FailingStreak": 15,
    "Log": [
        {
            "Start": "2025-01-22T14:44:33.72984062+08:00",
            "End": "2025-01-22T14:44:33.756377598+08:00",
            "ExitCode": -1,
            "Output": "OCI runtime exec failed: exec failed: unable to start container process: exec: \"curl\": executable file not found in $PATH: unknown"
        },
        {
            "Start": "2025-01-22T14:45:33.757193889+08:00",
            "End": "2025-01-22T14:45:33.785556044+08:00",
            "ExitCode": -1,
            "Output": "OCI runtime exec failed: exec failed: unable to start container process: exec: \"curl\": executable file not found in $PATH: unknown"
        },
        {
            "Start": "2025-01-22T14:46:33.786507659+08:00",
            "End": "2025-01-22T14:46:33.811238125+08:00",
            "ExitCode": -1,
            "Output": "OCI runtime exec failed: exec failed: unable to start container process: exec: \"curl\": executable file not found in $PATH: unknown"
        },
        {
            "Start": "2025-01-22T14:47:33.811518933+08:00",
            "End": "2025-01-22T14:47:33.839010734+08:00",
            "ExitCode": -1,
            "Output": "OCI runtime exec failed: exec failed: unable to start container process: exec: \"curl\": executable file not found in $PATH: unknown"
        },
        {
            "Start": "2025-01-22T14:48:33.839589519+08:00",
            "End": "2025-01-22T14:48:33.865899845+08:00",
            "ExitCode": -1,
            "Output": "OCI runtime exec failed: exec failed: unable to start container process: exec: \"curl\": executable file not found in $PATH: unknown"
        }
    ]
}
```

这样我们就可以明确知道，这是因为没有安装 `curl`。
