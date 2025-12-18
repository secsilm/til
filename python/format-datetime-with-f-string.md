# 使用 f-string 格式化日期时间

在昨天与 chatgpt 的交流过程中，学到了还能**通过 f-string 来格式化日期时间**：

```python
>>> from datetime import datetime
>>> now = datetime.now()
>>> f"{now:%y-%m-%d}"
'25-12-18'
>>> f"{now:%Y-%m-%d %H:%M:%S.%f}"
'2025-12-18 10:07:41.389265'
```

我是 f-string 的忠实用户，这下方便多了，之前老是有点分不清格式化时间的时候到底应该用 `strftime` 还是 `strptime`（后来记住了，包含 `f` 的就是格式化 format 时间的），现在直接 f-string，简洁还统一。f-string 真是强大。

实际上所有实现了 `__format__` 方法的对象都可以放到 f-string 里。
