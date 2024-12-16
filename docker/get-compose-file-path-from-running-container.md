# 获取正在运行的 container 的 compose 文件路径

假设我们想要知道目前在运行的一个 docker container，是从哪个 compose 文件启动的，我们可以使用 `docker inspect` 来获取：

```bash
$ docker inspect {container_id} | grep com.docker.compose
                "com.docker.compose.config-hash": "3a2c0f6d660cff04c56ac71abc0adc6afec9b87563de4ff233d2c13f466ca9f4",
                "com.docker.compose.container-number": "1",
                "com.docker.compose.depends_on": "prometheus:service_started:false",
                "com.docker.compose.image": "sha256:5c0692a901547aefc789c745df29d2ab136cfee24b10ad33c1509b67fb6ed024",
                "com.docker.compose.oneoff": "False",
                "com.docker.compose.project": "monitor",
                "com.docker.compose.project.config_files": "/some/path/docker-compose.yml",
                "com.docker.compose.project.working_dir": "/some/path",
                "com.docker.compose.service": "grafana",
                "com.docker.compose.version": "2.21.0"
```

## References

- [Get docker-compose.yml file location from running container? - Stack Overflow](https://stackoverflow.com/a/63788532)
