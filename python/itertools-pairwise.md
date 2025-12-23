# 使用 `itertools.pairwise` 进行相邻元素对儿遍历

相邻元素对儿遍历指的是给定一个输入列表，输出所有相邻元素对儿。例如，输入 `['a', 'b', 'c']`，输出 `[('a', 'b'), ('b', 'c')]`。

我们有多种方式可以实现，例如使用 `zip(lst[:-1], lst[1:])`，或者 `for i, right in enumerate(lst[1:], start=1)`。除此之外，我们还有一种更为简洁和高效的写法：使用 `itertools.pairwise`：


```python
>>> from itertools import pairwise
>>> list(pairwise(['a', 'b', 'c']))
[('a', 'b'), ('b', 'c')]  
```

根据 [python 文档](https://docs.python.org/3/library/itertools.html#itertools.pairwise)，该函数的大致实现逻辑如下，无需使用切片，而是使用 iterator：

```python
def pairwise(iterable):
    # pairwise('ABCDEFG') → AB BC CD DE EF FG

    iterator = iter(iterable)
    a = next(iterator, None)

    for b in iterator:
        yield a, b
        a = b
```

注意该函数是在 python3.10 引入的。
