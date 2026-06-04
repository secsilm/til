# 排查并清理 Langfuse ClickHouse 和 Minio 磁盘占用过大的问题

> 本文由 ChatGPT 5.5 Thinking 总结自我和它之间的对话，未经严格人工校验。

今天排查了 Langfuse 自托管环境中 ClickHouse 磁盘占用过大的问题。现象是 ClickHouse 数据目录占用明显偏高，进一步查看后发现主要不是业务主表，而是 ClickHouse 系统日志表和 Langfuse 的 blob 索引表。

## 1. 查看各表磁盘占用

进入 ClickHouse 后执行：

```sql
SELECT
    database,
    table,
    formatReadableSize(sum(bytes)) AS total_size,
    sum(rows) AS total_rows,
    max(toTimeZone(modification_time, 'Asia/Shanghai')) AS last_updated_bj_time
FROM system.parts
WHERE active
GROUP BY database, table
ORDER BY sum(bytes) DESC
FORMAT Pretty;
```

作用：

- 查看每张表的物理占用；
- 查看行数；
- 查看最近更新时间，并统一转为北京时间。

结果发现 `system.text_log`、`system.trace_log`、`system.query_log`、`system.opentelemetry_span_log` 等系统日志表占用了大量空间。

## 2. 清理 ClickHouse 系统日志表

对于明显不再写入的大日志表，可以执行：

```sql
SET max_table_size_to_drop = 0;
SET max_partition_size_to_drop = 0;

TRUNCATE TABLE system.text_log;
TRUNCATE TABLE system.trace_log;
TRUNCATE TABLE system.opentelemetry_span_log;
TRUNCATE TABLE system.query_log;
TRUNCATE TABLE system.metric_log;
TRUNCATE TABLE system.asynchronous_metric_log;
TRUNCATE TABLE system.query_views_log;
TRUNCATE TABLE system.query_metric_log;
```

说明：

- `TRUNCATE TABLE` 用于清空整张表的数据，但保留表结构；
- 相比 `DELETE FROM ... WHERE 1`，`TRUNCATE` 更适合清理整张大表；
- ClickHouse 默认会限制过大的表执行 `DROP` / `TRUNCATE`；
- `max_table_size_to_drop = 0` 和 `max_partition_size_to_drop = 0` 用于临时取消当前 session 的大小限制；
- 这两个 `SET` 只对当前连接生效，不会持久保存。

系统日志表清理后，磁盘占用明显下降。

## 3. 处理仍在增长的 `part_log`

清理后发现 `system.part_log` 仍然较大，并且持续更新。

`part_log` 是 ClickHouse 记录 MergeTree 数据 part 事件的系统日志表，例如：

- 新 part 写入；
- part merge；
- TTL 删除；
- mutation；
- part 删除或移动。

它不属于业务数据，可以安全清理。相比完全禁用，保留短 TTL 更适合保留少量诊断能力：

```sql
ALTER TABLE system.part_log
MODIFY TTL event_date + INTERVAL 3 DAY DELETE;
```

同时可以给其他系统日志表设置 TTL：

```sql
ALTER TABLE system.latency_log
MODIFY TTL event_date + INTERVAL 3 DAY DELETE;

ALTER TABLE system.error_log
MODIFY TTL event_date + INTERVAL 7 DAY DELETE;
```

作用：

- 保留最近几天的诊断信息；
- 避免系统日志长期膨胀。

## 4. 处理 `blob_storage_file_log`

业务表中发现：

```text
default.blob_storage_file_log
```

占用较大。它不是 ClickHouse 系统日志表，而是 Langfuse 用来记录 S3/MinIO blob 文件的索引表。

查看表结构发现它没有 TTL：

```sql
CREATE TABLE default.blob_storage_file_log
(
    ...
    created_at DateTime64(3),
    event_ts DateTime64(3),
    ...
)
ENGINE = ReplacingMergeTree(event_ts, is_deleted)
ORDER BY (project_id, entity_type, entity_id, event_id)
```

进一步按 `entity_type` 查看分布：

```sql
SELECT
    entity_type,
    count() AS total_rows,
    formatReadableSize(sum(length(bucket_path))) AS approx_path_size,
    min(toTimeZone(created_at, 'Asia/Shanghai')) AS min_created_at,
    max(toTimeZone(created_at, 'Asia/Shanghai')) AS max_created_at,
    min(toTimeZone(event_ts, 'Asia/Shanghai')) AS min_event_ts,
    max(toTimeZone(event_ts, 'Asia/Shanghai')) AS max_event_ts
FROM default.blob_storage_file_log
GROUP BY entity_type
ORDER BY total_rows DESC
FORMAT Pretty;
```

还可以查看删除标记分布：

```sql
SELECT
    entity_type,
    is_deleted,
    count() AS total_rows,
    min(toTimeZone(event_ts, 'Asia/Shanghai')) AS min_event_ts,
    max(toTimeZone(event_ts, 'Asia/Shanghai')) AS max_event_ts
FROM default.blob_storage_file_log
GROUP BY entity_type, is_deleted
ORDER BY entity_type, is_deleted
FORMAT Pretty;
```

排查发现：

- `trace` 仍然持续写入；
- `observation` 和 `score` 已经停写；
- 但不应直接 `TRUNCATE` 整张表，因为 `trace` 仍然是有效数据。

根据 Langfuse 文档，`blob_storage_file_log` 可以设置 TTL，并与对象存储的 lifecycle 保持一致。因此设置为 60 天：

```sql
ALTER TABLE default.blob_storage_file_log
MODIFY TTL toDateTime(created_at) + INTERVAL 60 DAY DELETE;
```

注意：

- `created_at` 是 `DateTime64(3)`；
- ClickHouse TTL 表达式需要 `Date` 或 `DateTime`；
- 所以需要用 `toDateTime(created_at)` 转换。

设置后，`blob_storage_file_log` 明显变小。

## 5. 给 MinIO 配置 lifecycle

当前部署中，ClickHouse 数据存储在本地目录：

```yaml
- /path/to/clickhouse/data:/var/lib/clickhouse
```

MinIO 只是 Langfuse 的 event/media blob storage：

```yaml
LANGFUSE_S3_EVENT_UPLOAD_BUCKET: <LANGFUSE_BUCKET>
LANGFUSE_S3_EVENT_UPLOAD_PREFIX: events/
```

所以可以给 MinIO bucket 配 lifecycle。执行：

```bash
mc alias set local http://localhost:9000 <MINIO_ACCESS_KEY> <MINIO_SECRET_KEY>
mc ilm rule add local/<LANGFUSE_BUCKET> --expire-days 60
mc ilm rule ls local/<LANGFUSE_BUCKET>
```

作用：

- 让 bucket 中超过 60 天的对象由 MinIO 后台自动过期删除；
- 与 ClickHouse 中 `blob_storage_file_log` 的 60 天 TTL 保持一致。

需要注意：

- MinIO lifecycle 不会立即删除所有历史对象；
- 它是后台异步清理；
- 对象数量很多时，释放空间需要等待一段时间。

## 6. 关于 ClickHouse 数据和 MinIO lifecycle 的区别

如果 ClickHouse 自己把对象存储作为磁盘使用，则不能直接给该对象存储配置删除型 lifecycle，否则可能绕过 ClickHouse 破坏数据一致性。

本次部署中，ClickHouse 数据目录是本地挂载：

```yaml
- /path/to/clickhouse/data:/var/lib/clickhouse
```

而 MinIO 是 Langfuse 的事件文件和媒体文件存储，因此可以对 MinIO bucket 设置 lifecycle，同时在 ClickHouse 中给 `blob_storage_file_log` 设置 TTL。

## 7. 最终策略

本次采用的策略是：

- ClickHouse 系统日志表：清理历史大表；
- `part_log` 等仍在增长的系统表：设置短 TTL；
- `blob_storage_file_log`：设置 60 天 TTL；
- MinIO bucket：设置 60 天 lifecycle；
- 不直接删除 ClickHouse 数据目录中的文件；
- 不直接 truncate Langfuse 业务表。

这类问题排查时，优先用 `system.parts` 找出大表，再区分系统日志表和业务表，避免误删业务数据。
