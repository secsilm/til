# 防止 pandas 误识别 NA 值

> TL;DR：只将空字符串识别为 na：`keep_default_na=False, na_values=['']`。

使用 pandas 读取 csv 文件时，有时会发现有些值被误识别为 na 了。比如我今天在读取一个国家代码和国家名的映射表时，发现纳米比亚的值总是缺失，检查一通才发现，是纳米比亚的代码 `NA` 被识别成了 na。之前我只知道空字符串会被识别为 na，没想到 `NA` 也会被识别为 na。

根据 [pandas 文档](https://pandas.pydata.org/docs/reference/api/pandas.read_csv.html)，以下值都会默认被识别为 na：

```python
[' ',
 '#N/A',
 '#N/A N/A',
 '#NA',
 '-1.#IND',
 '-1.#QNAN',
 '-NaN',
 '-nan',
 '1.#IND',
 '1.#QNAN',
 '<NA>',
 'N/A',
 'NA',
 'NULL',
 'NaN',
 'None',
 'n/a',
 'nan',
 'null']
```

涉及到 na 识别的参数有这么几个：

- na_values：用于指定哪些是 na，默认就是上面列举的那几个。
- keep_default_na：是否使用默认的 na values，默认 `True`。
- na_filter：是否检测 na，默认 `True`。如果你确认文件里没有 na，那么你可以设为 `False` 来提升加载速度。

文档上说可以结合使用 `dtype=str` 和 `na_values` 来避免误识别，比如指定 `na_values=['']`，但实际上不行，因为有如下的规则：

> - If `keep_default_na` is `True`, and `na_values` are specified, `na_values` is appended to the default `NaN` values used for parsing.
> - If `keep_default_na` is `True`, and `na_values` are not specified, only the default `NaN` values are used for parsing.
> - If `keep_default_na` is `False`, and `na_values` are specified, only the `NaN` values specified na_values are used for parsing.
> - If `keep_default_na` is `False`, and `na_values` are not specified, no strings will be parsed as `NaN`.
> 
> Note that if `na_filter` is passed in as `False`, the `keep_default_na` and `na_values` parameters will be ignored.

关键就在于第一条，如果 `keep_default_na=True`，那么你指定的 `na_values` 的值就是 append 进去的，而不是直接替代。

所以要实现 `NA` 不要识别成 na，同时又想要保证空字符串要识别成 na，我们**需要结合 `keep_default_na` 和 `na_values`**：

```python
df = pd.read_csv(datafile, sep='\t', keep_default_na=False, na_values=[''])
```

这样就只有空字符串被识别为 na 了。
