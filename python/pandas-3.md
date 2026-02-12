# pandas 3 的新变化

pandas 于 2026-01-21 [发布了 3.0 版本](https://pandas.pydata.org/docs/whatsnew/v3.0.0.html)，感觉变化好快，还记得 2.x 版本才刚出没多久，一查果然，直接从 2.3 蹦到 3.0 了：

<img width="521" height="690" alt="image" src="https://github.com/user-attachments/assets/1ce9cb03-821e-433d-9d9f-394093f69be7" />

这次的新版本主要有两个大变动：引入 str 类型和 CoW 成为默认模式（会比较大影响取值赋值操作）。

## 全字符串列的 dtype 现在为 str

之前这种列的类型为 `object`，实际上为 numpy 的 `object` 类型，一大好处是可以 hold 各种类型的 python 对象。现在纯 str 数据会被直接转为 [`pandas.StringDtype`](https://pandas.pydata.org/docs/reference/api/pandas.StringDtype.html#pandas.StringDtype) 类型，其他特殊类型（比如 list）仍然为 `object`：

```python
In [23]: pd.Series(["a", "b"])
Out[23]: 
0    a
1    b
dtype: str
```

这种新类型现在会*优先*由 `pyarrow` 提供支持（更好的性能），但是由于 `pyarrow` 不是 pandas 的必选依赖，所以建议手动安装。

在使用 `.select_dtypes` 时，可以传入 `str` 或者 `string`：`df.select_dtypes(include=['str'])`。

## str 列的缺失值永远为 `NaN`

```python
In [22]: pd.Series(["a", "b", None])
Out[22]: 
0      a
1      b
2    NaN
dtype: str
```

注意如果列类型为 `object`，那么 `None` 仍然保持原样。所以在 pandas 中判断缺失值时，最好使用 `.isna()`/`.notna()` 方法。

## 在 str 列添加非 str 数据会报错

```python
In [24]: ser = pd.Series(["a", "b"])

In [25]: ser[0] = 1
---------------------------------------------------------------------------
TypeError                                 Traceback (most recent call last)
File ~/miniconda3/envs/pandas3/lib/python3.13/site-packages/pandas/core/series.py:1090, in Series.__setitem__(self, key, value)
   1089 try:
-> 1090     self._set_with_engine(key, value)
   1091 except KeyError:
   1092     # We have a scalar (or for MultiIndex or object-dtype, scalar-like)
   1093     #  key that is not present in self.index.
   1094     # GH#12862 adding a new key to the Series

File ~/miniconda3/envs/pandas3/lib/python3.13/site-packages/pandas/core/series.py:1143, in Series._set_with_engine(self, key, value)
   1142 # this is equivalent to self._values[key] = value
-> 1143 self._mgr.setitem_inplace(loc, value)

File ~/miniconda3/envs/pandas3/lib/python3.13/site-packages/pandas/core/internals/managers.py:2209, in SingleBlockManager.setitem_inplace(self, indexer, value)
   2207     value = value[0, ...]
-> 2209 arr[indexer] = value

File ~/miniconda3/envs/pandas3/lib/python3.13/site-packages/pandas/core/arrays/string_.py:863, in StringArray.__setitem__(self, key, value)
    861     raise ValueError("Cannot modify read-only array")
--> 863 value = self._maybe_convert_setitem_value(value)
    865 key = check_array_indexer(self, key)

File ~/miniconda3/envs/pandas3/lib/python3.13/site-packages/pandas/core/arrays/string_.py:837, in StringArray._maybe_convert_setitem_value(self, value)
    836     elif not isinstance(value, str):
--> 837         raise TypeError(
    838             f"Invalid value '{value}' for dtype '{self.dtype}'. Value should "
    839             f"be a string or missing value, got '{type(value).__name__}' "
    840             "instead."
    841         )
    842 else:

TypeError: Invalid value '1' for dtype 'str'. Value should be a string or missing value, got 'int' instead.

During handling of the above exception, another exception occurred:

TypeError                                 Traceback (most recent call last)
Cell In[25], line 1
----> 1 ser[0] = 1

File ~/miniconda3/envs/pandas3/lib/python3.13/site-packages/pandas/core/series.py:1100, in Series.__setitem__(self, key, value)
   1097 except (TypeError, ValueError, LossySetitemError):
   1098     # The key was OK, but we cannot set the value losslessly
   1099     indexer = self.index.get_loc(key)
-> 1100     self._set_values(indexer, value)
   1102 except InvalidIndexError as err:
   1103     if isinstance(key, tuple) and not isinstance(self.index, MultiIndex):
   1104         # cases with MultiIndex don't get here bc they raise KeyError
   1105         # e.g. test_basic_getitem_setitem_corner

File ~/miniconda3/envs/pandas3/lib/python3.13/site-packages/pandas/core/series.py:1168, in Series._set_values(self, key, value)
   1165 if isinstance(key, (Index, Series)):
   1166     key = key._values
-> 1168 self._mgr = self._mgr.setitem(indexer=key, value=value)

File ~/miniconda3/envs/pandas3/lib/python3.13/site-packages/pandas/core/internals/managers.py:604, in BaseBlockManager.setitem(self, indexer, value)
    600     # No need to split if we either set all columns or on a single block
    601     # manager
    602     self = self.copy(deep=True)
--> 604 return self.apply("setitem", indexer=indexer, value=value)

File ~/miniconda3/envs/pandas3/lib/python3.13/site-packages/pandas/core/internals/managers.py:442, in BaseBlockManager.apply(self, f, align_keys, **kwargs)
    440         applied = b.apply(f, **kwargs)
    441     else:
--> 442         applied = getattr(b, f)(**kwargs)
    443     result_blocks = extend_blocks(applied, result_blocks)
    445 out = type(self).from_blocks(result_blocks, [ax.view() for ax in self.axes])

File ~/miniconda3/envs/pandas3/lib/python3.13/site-packages/pandas/core/internals/blocks.py:1667, in EABackedBlock.setitem(self, indexer, value)
   1664 check_setitem_lengths(indexer, value, values)
   1666 try:
-> 1667     values[indexer] = value
   1668 except (ValueError, TypeError):
   1669     if isinstance(self.dtype, IntervalDtype):
   1670         # see TestSetitemFloatIntervalWithIntIntervalValues

File ~/miniconda3/envs/pandas3/lib/python3.13/site-packages/pandas/core/arrays/string_.py:863, in StringArray.__setitem__(self, key, value)
    860 if self._readonly:
    861     raise ValueError("Cannot modify read-only array")
--> 863 value = self._maybe_convert_setitem_value(value)
    865 key = check_array_indexer(self, key)
    866 scalar_key = lib.is_scalar(key)

File ~/miniconda3/envs/pandas3/lib/python3.13/site-packages/pandas/core/arrays/string_.py:837, in StringArray._maybe_convert_setitem_value(self, value)
    835         value = self.dtype.na_value
    836     elif not isinstance(value, str):
--> 837         raise TypeError(
    838             f"Invalid value '{value}' for dtype '{self.dtype}'. Value should "
    839             f"be a string or missing value, got '{type(value).__name__}' "
    840             "instead."
    841         )
    842 else:
    843     value = extract_array(value, extract_numpy=True)

TypeError: Invalid value '1' for dtype 'str'. Value should be a string or missing value, got 'int' instead.
```

解决方法就是用 `.astype("object")` 转为 `object` 类型。

## `.to_numpy()` 返回的是一个只读对象

```python
# 2.2.3
>>> ser = pd.Series([1, 2, 3])
>>> a = ser.to_numpy()
>>> a[0] = 100
>>> ser
0    100
1      2
2      3
dtype: int64

# 3.0
>>> a[0] = 100
---------------------------------------------------------------------------
ValueError                                Traceback (most recent call last)
Cell In[7], line 1
----> 1 a[0] = 100

ValueError: assignment destination is read-only
```

## 链式赋值不再生效

```python
# 2.2.3
In [22]: df = pd.DataFrame({"foo": [1, 2, 3], "bar": [4, 5, 6]})

In [23]: df["foo"][df["bar"] > 5] = 100
<ipython-input-23-180c13c8363c>:1: FutureWarning: ChainedAssignmentError: behaviour will change in pandas 3.0!
You are setting values through chained assignment. Currently this works in certain cases, but when using Copy-on-Write (which will become the default behaviour in pandas 3.0) this will never work to update the original DataFrame or Series, because the intermediate object on which we are setting values will behave as a copy.
A typical example is when you are setting values in a column of a DataFrame, like:

df["col"][row_indexer] = value

Use `df.loc[row_indexer, "col"] = values` instead, to perform the assignment in a single step and ensure this keeps updating the original `df`.

See the caveats in the documentation: https://pandas.pydata.org/pandas-docs/stable/user_guide/indexing.html#returning-a-view-versus-a-copy

  df["foo"][df["bar"] > 5] = 100

In [24]: df
Out[24]: 
   foo  bar
0    1    4
1    2    5
2  100    6

# 3.0
In [13]: df = pd.DataFrame({"foo": [1, 2, 3], "bar": [4, 5, 6]})

In [14]: df["foo"][df["bar"] > 5] = 100
<ipython-input-14-180c13c8363c>:1: ChainedAssignmentError: A value is being set on a copy of a DataFrame or Series through chained assignment.
Such chained assignment never works to update the original DataFrame or Series, because the intermediate object on which we are setting values always behaves as a copy (due to Copy-on-Write).

Try using '.loc[row_indexer, col_indexer] = value' instead, to perform the assignment in a single step.

See the documentation for a more detailed explanation: https://pandas.pydata.org/pandas-docs/stable/user_guide/copy_on_write.html#chained-assignment
  df["foo"][df["bar"] > 5] = 100

In [15]: df
Out[15]: 
   foo  bar
0    1    4
1    2    5
2    3    6
```

可以看到 2.2.3 版本虽然报了 warning，但是仍然是生效的。而 3.0 版本则抛出 `ChainedAssignmentError`，且原 df 并未修改。所以尽量避免使用这种链式赋值，尽量使用 `.loc`：

```python
In [35]: df.loc[df["bar"] > 5, "foo"] = 100
```

## References

- [Migration guide for the new string data type (pandas 3.0) — pandas 3.0.0 documentation](https://pandas.pydata.org/docs/user_guide/migration-3-strings.html)
- [Copy-on-Write (CoW) — pandas 3.0.0 documentation](https://pandas.pydata.org/docs/user_guide/copy_on_write.html)
