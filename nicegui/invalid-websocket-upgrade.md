# NiceGUI 报错 Invalid websocket upgrade

最近在用 nicegui 来构建内部工具，左右布局，左侧是 tab 页导航栏，右侧是 tab 页内容。niucegui 比 gradio 灵活多了，而且界面也更好看、更现代。

我在本地运行时没问题，但是到线上后发现界面可以打开，但是点击其他 tab 页时无反应，无法切换到其他 tab 页。同时询问 chatgpt 和 google 搜索，google 搜索很快就找到了一条 github issue：[Invalid websocket upgrade · Issue #2781 · zauberzeug/nicegui](https://github.com/zauberzeug/nicegui/issues/2781) 。

该 issue 显示，出现这个错误的原因是 **nginx 缺少相关配置**，将以下三行加入 nginx 配置即可：

```
proxy_http_version 1.1;
proxy_set_header Upgrade $http_upgrade;
proxy_set_header Connection "Upgrade";
```

我对 nginx 一窍不通，以下是 chatgpt 5.1 的解释：

> 这是 Nginx 反向代理里，**支持协议升级（比如 WebSocket）** 时常见的一段配置。逐行解释：
> 
> 1. `proxy_http_version 1.1;`
> 
>    * 把 Nginx 与后端 upstream 通信时使用的 HTTP 版本改为 **1.1**。
>    * HTTP/1.0 不支持长连接和 `Upgrade` 机制，WebSocket 等协议升级一般需要 HTTP/1.1。
> 
> 2. `proxy_set_header Upgrade $http_upgrade;`
> 
>    * 把客户端请求中携带的 `Upgrade` 头（如 `Upgrade: websocket`）原样转发给后端。
>    * `$http_upgrade` 是 Nginx 内置变量，对应客户端请求的 `Upgrade` 头值。
>    * 用于告诉后端：“我要把当前 HTTP 连接升级成某种新协议（比如 WebSocket）”。
> 
> 3. `proxy_set_header Connection "Upgrade";`
> 
>    * 把发给后端的 `Connection` 头固定设置为 `Upgrade`。
>    * 与 `Upgrade` 头配合使用，含义是：
> 
>      > 这次连接要进行协议升级，请按 `Upgrade` 头里说明的协议来处理。
>    * 这是完成 HTTP ➝ WebSocket 等协议升级的必要条件之一。
> 
> 综合起来：
> 这三行是为了让 **Nginx 在做反向代理时，支持客户端发起的协议升级（最常见是 WebSocket）**，把升级相关的头信息正确地转发给后端服务。
