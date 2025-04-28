# pandas 中的时区转换

> TL;DR：`pd.to_datetime` -> `tz_localize` -> `tz_convert`。  

假设我们有一个时间字符串：`2025-04-28 11:51:10.389049`，而且已知表示的是北京时间，我们需要将其转为纽约时间。我们可以利用 pandas 和 zoneinfo（3.9 引入）来完成。

```python
In [1]: import pandas as pd

In [2]: timestr = '2025-04-28 11:51:10.389049'

In [3]: # 使用 to_datetime 转为 pandas 中的 Timestamp 对象
   ...: timeobj = pd.to_datetime(timestr)

In [4]: timeobj
Out[4]: Timestamp('2025-04-28 11:51:10.389049')  # 可以看到此时还不带时区信息，默认是时区无关的。

In [13]: timeobj_bj = timeobj.tz_localize(tz=ZoneInfo('Asia/Shanghai'))  # 加上时区信息，表明这是一个北京时间的时间对象。

In [14]: timeobj_bj
Out[14]: Timestamp('2025-04-28 11:51:10.389049+0800', tz='Asia/Shanghai')

In [15]: timeobj_bj.tz_convert(tz=ZoneInfo('America/New_York'))  # 再转为纽约时间。
Out[15]: Timestamp('2025-04-27 23:51:10.389049-0400', tz='America/New_York')
```

有几个需要注意的点：

1. 以上的时区信息除了可以使用 `ZoneInfo`，也可以直接使用字符串，也可以使用 `pytz.timezone('Asia/Shanghai')`。你可以使用 `zoneinfo.available_timezones()` 或者 `pytz.all_timezones` 来获取所有时区。
2. 如果你拿到的是一个 Series，那么需要先 `.dt`：`pd.to_datetime(column_name).dt.tz_localize(src_tz).tz_convert(tgt_tz)`。
3. 如果你拿到的是一个 DatetimeIndex，那么无需 `.dt`。
