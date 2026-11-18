# 为 langfuse clickhouse 设置 ttl

langfuse oss 版本是没有 ttl 的（企业版有），我们需要手动设置 5 张表（对于 V4 版本）的 ttl，否则持续增多的数据可能会吃满我们的硬盘。比如我们设为 3 个月：

1. 进入 ch 容器后执行 `clickhouse-client` 以进入数据库，这里省略掉 `--user` 和 `--password` 是因为 env 里已经配置了，我们的数据库也是默认的 `default` ，所以也不用指定 `--database` 。然后可以执行 `select current_user, current_database;` 来确认当前环境：

    ```sql
    clickhouse :) select current_user, current_database;
    
    SELECT
        current_user,
        current_database
    
    Query id: 47bf664d-e5b8-4c66-aa04-5bc6f9e11374
    
       ┌─current_user─┬─current_database─┐
    1. │ clickhouse   │ default          │
       └──────────────┴──────────────────┘
    
    1 row in set. Elapsed: 0.115 sec.
    ```

2. 执行 `ALTER` 语句以设置 ttl，可以挨个执行，执行完后可能需要较长时间才能结束：

    ```sql
    ALTER TABLE default.events_full
        MODIFY TTL toDateTime(start_time) + INTERVAL 3 MONTH DELETE;
    
    ALTER TABLE default.events_core
        MODIFY TTL toDateTime(start_time) + INTERVAL 3 MONTH DELETE;
    
    ALTER TABLE default.observations
        MODIFY TTL toDateTime(start_time) + INTERVAL 3 MONTH DELETE;
    
    ALTER TABLE default.traces
        MODIFY TTL toDateTime(timestamp) + INTERVAL 3 MONTH DELETE;
    
    ALTER TABLE default.scores
        MODIFY TTL toDateTime(timestamp) + INTERVAL 3 MONTH DELETE;
    ```

3. 确认设置成功，在结果里找 \``toIntervalMonth(3)` 即可：

    ```sql
    clickhouse :) SELECT name, engine_full
    FROM system.tables
    WHERE database = 'default'
      AND name IN ('events_full', 'events_core', 'observations', 'traces', 'scores')
    ORDER BY name
    FORMAT Vertical;
    
    SELECT
        name,
        engine_full
    FROM system.tables
    WHERE (database = 'default') AND (name IN ('events_full', 'events_core', 'observations', 'traces', 'scores'))
    ORDER BY name ASC
    FORMAT Vertical
    
    Query id: 773c5637-c7f6-4276-b451-4bbaaab7d5e3
    
    Row 1:
    ──────
    name:        events_core
    engine_full: ReplacingMergeTree(event_ts, is_deleted) PARTITION BY toYYYYMM(start_time) PRIMARY KEY (project_id, toStartOfMinute(start_time), xxHash32(trace_id)) ORDER BY (project_id, toStartOfMinute(start_time), xxHash32(trace_id), span_id, start_time) SAMPLE BY xxHash32(trace_id) TTL toDateTime(start_time) + toIntervalMonth(3) SETTINGS enable_block_number_column = 1, enable_block_offset_column = 1, prewarm_mark_cache = 1, prewarm_primary_key_cache = 1, index_granularity = 8192
    
    Row 2:
    ──────
    name:        events_full
    engine_full: ReplacingMergeTree(event_ts, is_deleted) PARTITION BY toYYYYMM(start_time) PRIMARY KEY (project_id, toStartOfMinute(start_time), xxHash32(trace_id)) ORDER BY (project_id, toStartOfMinute(start_time), xxHash32(trace_id), span_id, start_time) SAMPLE BY xxHash32(trace_id) TTL toDateTime(start_time) + toIntervalMonth(3) SETTINGS index_granularity_bytes = '64Mi', merge_max_block_size_bytes = '64Mi', enable_block_number_column = 1, enable_block_offset_column = 1, prewarm_mark_cache = 1, prewarm_primary_key_cache = 1, index_granularity = 8192
    
    Row 3:
    ──────
    name:        observations
    engine_full: ReplacingMergeTree(event_ts, is_deleted) PARTITION BY toYYYYMM(start_time) PRIMARY KEY (project_id, type, toDate(start_time)) ORDER BY (project_id, type, toDate(start_time), id) TTL toDateTime(start_time) + toIntervalMonth(3) SETTINGS index_granularity = 8192
    
    Row 4:
    ──────
    name:        scores
    engine_full: ReplacingMergeTree(event_ts, is_deleted) PARTITION BY toYYYYMM(timestamp) PRIMARY KEY (project_id, toDate(timestamp), name) ORDER BY (project_id, toDate(timestamp), name, id) TTL toDateTime(timestamp) + toIntervalMonth(3) SETTINGS index_granularity = 8192, enable_block_number_column = 1, enable_block_offset_column = 1
    
    Row 5:
    ──────
    name:        traces
    engine_full: ReplacingMergeTree(event_ts, is_deleted) PARTITION BY toYYYYMM(timestamp) PRIMARY KEY (project_id, toDate(timestamp)) ORDER BY (project_id, toDate(timestamp), id) TTL toDateTime(timestamp) + toIntervalMonth(3) SETTINGS index_granularity = 8192
    
    5 rows in set. Elapsed: 0.098 sec.
    ```
