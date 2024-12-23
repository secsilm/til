# try/finally 的执行逻辑

Python 中的 `try` 有一个 `finally` 语句，主要用来 clean up。之前我仅仅是知道无论 `try` 语句块内容是否正常执行完毕，该语句**最终**都会被执行，也就是 `finally` 的字面意思，

但是这个**最终**，也包括 `try` 中包含一个 `return` 语句时，甚至 `continue` 和 `break`。

看下面几个例子：

```python
In [2]: def divide(a, b):
   ...:     try:
   ...:         return a/b
   ...:     finally:
   ...:         print('finally done')
   ...: 

In [3]: divide(2, 1)
finally done                # <-- finally 中的 print 也被执行了。
Out[3]: 2.0

In [4]: divide(2, 0)
finally done                # <-- finally 中的 print 也被执行了。
---------------------------------------------------------------------------
ZeroDivisionError                         Traceback (most recent call last)
Cell In[4], line 1
----> 1 divide(2, 0)

Cell In[2], line 3, in divide(a, b)
      1 def divide(a, b):
      2     try:
----> 3         return a/b
      4     finally:
      5         print('finally done')

ZeroDivisionError: division by zero
```

但是要注意一个函数只能触发一次 return，在 `finally` 中谨慎使用 `return`、`continue`、`break`：

> If the finally clause executes a return, break or continue statement, the saved exception is discarded.

```python
In [5]: def divide(a, b):
   ...:     try:
   ...:         return a/b
   ...:     finally:
   ...:         return 'finally done'
   ...: 

In [6]: divide(2, 1)
Out[6]: 'finally done'    # <-- 并没有返回 1

In [7]: divide(2, 0)
Out[7]: 'finally done'    # <-- 并没有抛出异常
```

所以 `finally` 最好只用来执行 clean up 操作，比如删除临时数据库表和关闭数据库连接等。

## References

- [8.4.4. finally clause — Python 3.13.1 documentation](https://docs.python.org/3/reference/compound_stmts.html#finally-clause)
- [python 3.x - Using "try"+"finally" without "except" never generates any error - Stack Overflow](https://stackoverflow.com/questions/61264374/using-tryfinally-without-except-never-generates-any-error)
