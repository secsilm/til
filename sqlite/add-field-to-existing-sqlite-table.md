# 增加新字段到现有数据库中，并设置默认值

假设我们有一个 sqlite 数据库 `feedbacks`，我们想要增加一个新的字段 `status`，并将默认值设为 0，现有 row 的 status 也全部设为 0。

那么我们可以使用 `sqlite3` 命令行工具进入数据库：

```bash
$ sqlite3 feedbacks.db
```

然后执行 sql 语句：

```bash
ALTER TABLE feedbacks ADD COLUMN status INTEGER DEFAULT 0;
```

如果要将全部 `status` 设为 0，那么：

```bash
UPDATE feedbacks SET status = 0;

# 确认是否设置成功
SELECT * FROM feedbacks WHERE status != 0;
```
