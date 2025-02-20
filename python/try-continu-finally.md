# finally 在 continue 后仍会执行

根据[文档](https://docs.python.org/3/reference/compound_stmts.html#finally-clause)：

> When a return, break or continue statement is executed in the try suite of a try…finally statement, the finally clause is also executed ‘on the way out.’

即在一个包含 try-except-finally 的循环块中，假如 `try` 中包含 `continue`，那么即使执行了 `continue`，那么 `finally` 块的语句也会被执行。

例如：

```python
>>> for i in range(1):
...     try:
...         continue
...     except Exception as e:
...         print('error')
...     finally:
...         print('finally')
... 
finally
```
