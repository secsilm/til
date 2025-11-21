# `nan` 比较与最大值陷阱

根据 [IEEE 754](https://zh.wikipedia.org/wiki/IEEE_754#%E6%B5%AE%E7%82%B9%E6%95%B0%E7%9A%84%E8%BF%90%E7%AE%97%E4%B8%8E%E5%87%BD%E6%95%B0)，`nan` 这个特殊值在进行比较时，有个比较大的坑，就是它**与任何值的比较结果都是 `False`**，所以就会导致下面这种情况：

```python
>>> a = float('nan')
>>> max(a, 1)
nan
>>> max(1, a)
1
```

Python 中 `max` 的比较逻辑是将第一个值设为默认最大值，与后续值逐个比较，如果 `current_value > max_value`（注意不是 `current_value < max_value`），那么就 `max_value = current_value`，然后与再后面的值进行比较。由于 `nan` 与任何值的比较都是 `False`，所以如果 `nan` 是第一个值，那么后面所有的 `current_value > max_value`（即 `nan`）都是 `False`，所以最大值就变成了 `nan`。

但是如果第一个值不是 `nan`，那么就正常了。通常我们需要的就是忽略 `nan` 值，此时我们可以使用 `np.nanmax`：

```python
>>> np.nanmax([a, 1])
1.0
>>> np.nanmax([1, a])
1.0
```

在 pandas 中，`nan` 是默认会被跳过的：

```python
>>> pd.Series([a, 1]).max()
1.0
>>> pd.Series([1, a]).max()
1.0
```

此外，`nan` 在 Python 中有三种形式：

- `float('nan')`
- `math.nan`
- `np.nan`

这三种形式是等价的（但并不意味着 `is` 为 `True`），在 pandas 中可以互换使用，不过一般建议使用 `np.nan`。

---

此外要注意，如果是一个包含 `None` 的列表，那么 `np.nanmax` 是会报错的，而 pd 不会：

```python
>>> data = [None, 3, 10, None, 7]
>>> np.nanmax(data)
TypeError                                 Traceback (most recent call last)
Cell In[6], line 1
----> 1 np.nanmax(data)

File <__array_function__ internals>:200, in nanmax(*args, **kwargs)
...

TypeError: '>=' not supported between instances of 'NoneType' and 'int'
>>> pd.Series(data).max()
10.0
>>> pd.Series(data).dtypes
dtype('float64')
>>> pd.Series(data)
0     NaN
1     3.0
2    10.0
3     NaN
4     7.0
dtype: float64
```

可以看到 pd 会自动转为 `float` 类型，而 np 则未经转换。所以想用 np 的话，也进行一次转换即可：

```python
>>> np.nanmax(np.array(data, dtype=float))
10.0
```
