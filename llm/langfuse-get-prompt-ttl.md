# langfuse 会在获取 prompt 失败时使用已缓存的结果

之前一直不太确定 langfuse 在获取 prompt 失败时会如何表现，直接报错还是使用之前缓存的结果（尽管该缓存已过期）。今天做了个实验，终于明白了，是会使用之前缓存的结果的。

我们可以使用如下程序 `langfuse_test.py`，该程序会缓存 120 秒获取到的 prompt：

```python
from config import langfuse
import time
from loguru import logger


if __name__ == "__main__":
    while 1:
        prompt = langfuse.get_prompt("my-prompt", cache_ttl_seconds=120)
        logger.info(f"Done getting {prompt=}.")
        time.sleep(10)
```

接下来：

1. 运行该程序，使 langfuse 成功获取到一次 prompt。
2. 关闭 langfuse 服务。
3. 观察该程序输出。

你会发现在 120 秒后，日志显示 langfuse 获取 prompt 失败了，但是它仍然返回了 prompt，注意该 prompt 对象的地址和之前是一样的，而且也有提示使用的是之前缓存的 prompt：

```python
2025-06-18 11:00:34.820 | INFO     | __main__:<module>:9 - Done getting prompt=<langfuse.model.TextPromptClient object at 0x7ff8eed969d0>.
2025-06-18 11:00:44.820 | INFO     | __main__:<module>:9 - Done getting prompt=<langfuse.model.TextPromptClient object at 0x7ff8eed969d0>.
2025-06-18 11:00:54.821 | INFO     | __main__:<module>:9 - Done getting prompt=<langfuse.model.TextPromptClient object at 0x7ff8eed969d0>.
2025-06-18 11:01:04.821 | INFO     | __main__:<module>:9 - Done getting prompt=<langfuse.model.TextPromptClient object at 0x7ff8eed969d0>.
2025-06-18 11:01:14.822 | INFO     | __main__:<module>:9 - Done getting prompt=<langfuse.model.TextPromptClient object at 0x7ff8eed969d0>.
2025-06-18 11:01:24.823 | INFO     | __main__:<module>:9 - Done getting prompt=<langfuse.model.TextPromptClient object at 0x7ff8eed969d0>.
2025-06-18 11:01:34.823 | INFO     | __main__:<module>:9 - Done getting prompt=<langfuse.model.TextPromptClient object at 0x7ff8eed969d0>.
2025-06-18 11:01:44.823 | INFO     | __main__:<module>:9 - Done getting prompt=<langfuse.model.TextPromptClient object at 0x7ff8eed969d0>.
2025-06-18 11:01:54.823 | INFO     | __main__:<module>:9 - Done getting prompt=<langfuse.model.TextPromptClient object at 0x7ff8eed969d0>.
2025-06-18 11:02:04.824 | INFO     | __main__:<module>:9 - Done getting prompt=<langfuse.model.TextPromptClient object at 0x7ff8eed969d0>.
2025-06-18 11:02:14.824 | INFO     | __main__:<module>:9 - Done getting prompt=<langfuse.model.TextPromptClient object at 0x7ff8eed969d0>.
2025-06-18 11:02:24.825 | INFO     | __main__:<module>:9 - Done getting prompt=<langfuse.model.TextPromptClient object at 0x7ff8eed969d0>.
2025-06-18 11:02:34.825 | INFO     | __main__:<module>:9 - Done getting prompt=<langfuse.model.TextPromptClient object at 0x7ff8eed969d0>.
Error while fetching prompt 'nc-gpt-35-turbo-label:production': [Errno 111] Connection refused
Traceback (most recent call last):
  File "/home/jy/miniconda3/lib/python3.11/site-packages/httpcore/_exceptions.py", line 10, in map_exceptions
    yield
  File "/home/jy/miniconda3/lib/python3.11/site-packages/httpcore/_backends/sync.py", line 212, in connect_tcp
    sock = socket.create_connection(
           ^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/jy/miniconda3/lib/python3.11/socket.py", line 851, in create_connection
    raise exceptions[0]
  File "/home/jy/miniconda3/lib/python3.11/socket.py", line 836, in create_connection
    sock.connect(sa)
ConnectionRefusedError: [Errno 111] Connection refused

The above exception was the direct cause of the following exception:

Traceback (most recent call last):
  File "/home/jy/miniconda3/lib/python3.11/site-packages/httpx/_transports/default.py", line 66, in map_httpcore_exceptions
    yield
  File "/home/jy/miniconda3/lib/python3.11/site-packages/httpx/_transports/default.py", line 228, in handle_request
    resp = self._pool.handle_request(req)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/jy/miniconda3/lib/python3.11/site-packages/httpcore/_sync/connection_pool.py", line 262, in handle_request
    raise exc
  File "/home/jy/miniconda3/lib/python3.11/site-packages/httpcore/_sync/connection_pool.py", line 245, in handle_request
    response = connection.handle_request(request)
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/jy/miniconda3/lib/python3.11/site-packages/httpcore/_sync/connection.py", line 99, in handle_request
    raise exc
  File "/home/jy/miniconda3/lib/python3.11/site-packages/httpcore/_sync/connection.py", line 76, in handle_request
    stream = self._connect(request)
             ^^^^^^^^^^^^^^^^^^^^^^
  File "/home/jy/miniconda3/lib/python3.11/site-packages/httpcore/_sync/connection.py", line 124, in _connect
    stream = self._network_backend.connect_tcp(**kwargs)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/jy/miniconda3/lib/python3.11/site-packages/httpcore/_backends/sync.py", line 211, in connect_tcp
    with map_exceptions(exc_map):
  File "/home/jy/miniconda3/lib/python3.11/contextlib.py", line 155, in __exit__
    self.gen.throw(typ, value, traceback)
  File "/home/jy/miniconda3/lib/python3.11/site-packages/httpcore/_exceptions.py", line 14, in map_exceptions
    raise to_exc(exc) from exc
httpcore.ConnectError: [Errno 111] Connection refused

The above exception was the direct cause of the following exception:

Traceback (most recent call last):
  File "/home/jy/miniconda3/lib/python3.11/site-packages/langfuse/client.py", line 1071, in _fetch_prompt_and_update_cache
    promptResponse = self.client.prompts.get(
                     ^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/jy/miniconda3/lib/python3.11/site-packages/langfuse/api/resources/prompts/client.py", line 66, in get
    _response = self._client_wrapper.httpx_client.request(
                ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/jy/miniconda3/lib/python3.11/site-packages/langfuse/api/core/http_client.py", line 100, in request
    response = self.httpx_client.request(*args, **kwargs)
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/jy/miniconda3/lib/python3.11/site-packages/httpx/_client.py", line 814, in request
    return self.send(request, auth=auth, follow_redirects=follow_redirects)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/jy/miniconda3/lib/python3.11/site-packages/httpx/_client.py", line 901, in send
    response = self._send_handling_auth(
               ^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/jy/miniconda3/lib/python3.11/site-packages/httpx/_client.py", line 929, in _send_handling_auth
    response = self._send_handling_redirects(
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/jy/miniconda3/lib/python3.11/site-packages/httpx/_client.py", line 966, in _send_handling_redirects
    response = self._send_single_request(request)
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/jy/miniconda3/lib/python3.11/site-packages/httpx/_client.py", line 1002, in _send_single_request
    response = transport.handle_request(request)
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/jy/miniconda3/lib/python3.11/site-packages/httpx/_transports/default.py", line 227, in handle_request
    with map_httpcore_exceptions():
  File "/home/jy/miniconda3/lib/python3.11/contextlib.py", line 155, in __exit__
    self.gen.throw(typ, value, traceback)
  File "/home/jy/miniconda3/lib/python3.11/site-packages/httpx/_transports/default.py", line 83, in map_httpcore_exceptions
    raise mapped_exc(message) from exc
httpx.ConnectError: [Errno 111] Connection refused
Returning expired prompt cache for 'nc-gpt-35-turbo-label:production' due to fetch error: [Errno 111] Connection refused  # <-- 注意这里的提示
2025-06-18 11:02:44.828 | INFO     | __main__:<module>:9 - Done getting prompt=<langfuse.model.TextPromptClient object at 0x7ff8eed969d0>.  # <-- 注意这里的 prompt 对象地址和之前是一样的
```
