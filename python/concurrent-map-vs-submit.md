# concurrent 中的 `map` 与 `submit`

两者都可以用来并行执行任务，两者的用法大致如下：

```python
from concurrent.futures import ThreadPoolExecutor


def square(x):
    return x * x


# List of numbers
numbers = [1, 2, 3, 4, 5]

# map
with ThreadPoolExecutor() as executor:
    results = executor.map(square, numbers)

# submit
with ThreadPoolExecutor() as executor:
    # Submit tasks and collect Future objects
    futures = [executor.submit(square, num) for num in numbers]
    
    # Wait for all futures to complete and get the results
    results = [future.result() for future in futures]
```

除了在写法上有区别，还有一些重要区别：

1. `map` 返回顺序与输出顺序一致，且需要等到所有结果都完成时才返回。而 `submit` 不是，谁先完成谁先返回，所以返回顺序可能与输入不一致。
2. 一旦任务函数（如例子中的 `square`）对某个输入有报错，那么整个 `map` 将会直接报错返回。而 `submit` 你可以单独处理某个输入的报错，不影响其他没报错的输入，只需用 try 块包住 `future.result()`。
3. `map` 内部也是调用的 `submit`：https://github.com/python/cpython/blob/388e1ca9f08ee5caefd1dd946dc6e236ce73d46f/Lib/concurrent/futures/_base.py#L600 。

所以说**两者的总执行时间是一样的**，只不过 `submit` 可以先返回已经完成的任务结果，所以**如果你需要任务完成后立即处理，那么使用 `submit`；如果你需要返回顺序与输入顺序一致，那么使用 `map`**。
