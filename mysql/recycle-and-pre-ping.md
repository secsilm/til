# MySQL 自动回收旧连接和 pre ping

我有一个队列消费程序，里面有一段使用 sqlalchemy 连接 MySQL 的代码：

```python
from sqlalchemy import create_engine
from sqlalchemy import text as sqlalchemy_text

engine = create_engine(
    f"mysql+pymysql://{config['user']}:{config['password']}@{config['host']}:{config['port']}/{config['db_name']}",
)
with self.engine.connect() as conn:
    sql = f"SELECT * FROM `{table_name}` WHERE `news_id`={news_id}"
    result = conn.execute(sqlalchemy_text(sql))
    for row in result.mappings():
        return SimpleNamespace(**row)
```

有次我启动了这个程序，然后在 1 天多的时间里，队列都是空闲的。然后队列里来了一条数据开始消费，结果报错：

```python
Traceback (most recent call last):
  File "/home/secsilm/miniconda3/lib/python3.11/site-packages/pymysql/connections.py", line 803, in _write_bytes
    self._sock.sendall(data)
BrokenPipeError: [Errno 32] Broken pipe

During handling of the above exception, another exception occurred:

Traceback (most recent call last):
  File "/home/secsilm/miniconda3/lib/python3.11/site-packages/sqlalchemy/engine/base.py", line 1970, in _exec_single_context
    self.dialect.do_execute(
  File "/home/secsilm/miniconda3/lib/python3.11/site-packages/sqlalchemy/engine/default.py", line 924, in do_execute
    cursor.execute(statement, parameters)
  File "/home/secsilm/miniconda3/lib/python3.11/site-packages/pymysql/cursors.py", line 153, in execute
    result = self._query(query)
             ^^^^^^^^^^^^^^^^^^
  File "/home/secsilm/miniconda3/lib/python3.11/site-packages/pymysql/cursors.py", line 322, in _query
    conn.query(q)
  File "/home/secsilm/miniconda3/lib/python3.11/site-packages/pymysql/connections.py", line 557, in query
    self._execute_command(COMMAND.COM_QUERY, sql)
  File "/home/secsilm/miniconda3/lib/python3.11/site-packages/pymysql/connections.py", line 861, in _execute_command
    self._write_bytes(packet)
  File "/home/secsilm/miniconda3/lib/python3.11/site-packages/pymysql/connections.py", line 806, in _write_bytes
    raise err.OperationalError(
pymysql.err.OperationalError: (2006, "MySQL server has gone away (BrokenPipeError(32, 'Broken pipe'))")

The above exception was the direct cause of the following exception:

Traceback (most recent call last):
  File "/home/secsilm/projects/secrect_project/secrect_project/db.py", line 379, in get_by_id_single
    result = conn.execute(sqlalchemy_text(sql))
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/secsilm/miniconda3/lib/python3.11/site-packages/sqlalchemy/engine/base.py", line 1421, in execute
    return meth(
           ^^^^^
  File "/home/secsilm/miniconda3/lib/python3.11/site-packages/sqlalchemy/sql/elements.py", line 514, in _execute_on_connection
    return connection._execute_clauseelement(
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/secsilm/miniconda3/lib/python3.11/site-packages/sqlalchemy/engine/base.py", line 1643, in _execute_clauseelement
    ret = self._execute_context(
          ^^^^^^^^^^^^^^^^^^^^^^
  File "/home/secsilm/miniconda3/lib/python3.11/site-packages/sqlalchemy/engine/base.py", line 1849, in _execute_context
    return self._exec_single_context(
           ^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/secsilm/miniconda3/lib/python3.11/site-packages/sqlalchemy/engine/base.py", line 1989, in _exec_single_context
    self._handle_dbapi_exception(
  File "/home/secsilm/miniconda3/lib/python3.11/site-packages/sqlalchemy/engine/base.py", line 2356, in _handle_dbapi_exception
    raise sqlalchemy_exception.with_traceback(exc_info[2]) from e
  File "/home/secsilm/miniconda3/lib/python3.11/site-packages/sqlalchemy/engine/base.py", line 1970, in _exec_single_context
    self.dialect.do_execute(
  File "/home/secsilm/miniconda3/lib/python3.11/site-packages/sqlalchemy/engine/default.py", line 924, in do_execute
    cursor.execute(statement, parameters)
  File "/home/secsilm/miniconda3/lib/python3.11/site-packages/pymysql/cursors.py", line 153, in execute
    result = self._query(query)
             ^^^^^^^^^^^^^^^^^^
  File "/home/secsilm/miniconda3/lib/python3.11/site-packages/pymysql/cursors.py", line 322, in _query
    conn.query(q)
  File "/home/secsilm/miniconda3/lib/python3.11/site-packages/pymysql/connections.py", line 557, in query
    self._execute_command(COMMAND.COM_QUERY, sql)
  File "/home/secsilm/miniconda3/lib/python3.11/site-packages/pymysql/connections.py", line 861, in _execute_command
    self._write_bytes(packet)
  File "/home/secsilm/miniconda3/lib/python3.11/site-packages/pymysql/connections.py", line 806, in _write_bytes
    raise err.OperationalError(
sqlalchemy.exc.OperationalError: (pymysql.err.OperationalError) (2006, "MySQL server has gone away (BrokenPipeError(32, 'Broken pipe'))")
[SQL: SELECT * FROM `news_detail_202505` WHERE `news_id`=975051643912810496]
(Background on this error at: https://sqlalche.me/e/20/e3q8)

During handling of the above exception, another exception occurred:

Traceback (most recent call last):
  File "/home/secsilm/miniconda3/lib/python3.11/site-packages/sqlalchemy/engine/base.py", line 1970, in _exec_single_context
    self.dialect.do_execute(
  File "/home/secsilm/miniconda3/lib/python3.11/site-packages/sqlalchemy/engine/default.py", line 924, in do_execute
    cursor.execute(statement, parameters)
  File "/home/secsilm/miniconda3/lib/python3.11/site-packages/pymysql/cursors.py", line 153, in execute
    result = self._query(query)
             ^^^^^^^^^^^^^^^^^^
  File "/home/secsilm/miniconda3/lib/python3.11/site-packages/pymysql/cursors.py", line 322, in _query
    conn.query(q)
  File "/home/secsilm/miniconda3/lib/python3.11/site-packages/pymysql/connections.py", line 558, in query
    self._affected_rows = self._read_query_result(unbuffered=unbuffered)
                          ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/secsilm/miniconda3/lib/python3.11/site-packages/pymysql/connections.py", line 822, in _read_query_result
    result.read()
  File "/home/secsilm/miniconda3/lib/python3.11/site-packages/pymysql/connections.py", line 1200, in read
    first_packet = self.connection._read_packet()
                   ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/secsilm/miniconda3/lib/python3.11/site-packages/pymysql/connections.py", line 772, in _read_packet
    packet.raise_for_error()
  File "/home/secsilm/miniconda3/lib/python3.11/site-packages/pymysql/protocol.py", line 221, in raise_for_error
    err.raise_mysql_exception(self._data)
  File "/home/secsilm/miniconda3/lib/python3.11/site-packages/pymysql/err.py", line 143, in raise_mysql_exception
    raise errorclass(errno, errval)
pymysql.err.ProgrammingError: (1064, "You have an error in your SQL syntax; check the manual that corresponds to your MySQL server version for the right syntax to use near '%s' at line 1")

The above exception was the direct cause of the following exception:

Traceback (most recent call last):
  File "/home/secsilm/projects/secrect_project/secrect_project/db.py", line 388, in get_by_id_single
    result = conn.execute(sqlalchemy_text(sql))
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/secsilm/miniconda3/lib/python3.11/site-packages/sqlalchemy/engine/base.py", line 1421, in execute
    return meth(
           ^^^^^
  File "/home/secsilm/miniconda3/lib/python3.11/site-packages/sqlalchemy/sql/elements.py", line 514, in _execute_on_connection
    return connection._execute_clauseelement(
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/secsilm/miniconda3/lib/python3.11/site-packages/sqlalchemy/engine/base.py", line 1643, in _execute_clauseelement
    ret = self._execute_context(
          ^^^^^^^^^^^^^^^^^^^^^^
  File "/home/secsilm/miniconda3/lib/python3.11/site-packages/sqlalchemy/engine/base.py", line 1849, in _execute_context
    return self._exec_single_context(
           ^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/secsilm/miniconda3/lib/python3.11/site-packages/sqlalchemy/engine/base.py", line 1989, in _exec_single_context
    self._handle_dbapi_exception(
  File "/home/secsilm/miniconda3/lib/python3.11/site-packages/sqlalchemy/engine/base.py", line 2356, in _handle_dbapi_exception
    raise sqlalchemy_exception.with_traceback(exc_info[2]) from e
  File "/home/secsilm/miniconda3/lib/python3.11/site-packages/sqlalchemy/engine/base.py", line 1970, in _exec_single_context
    self.dialect.do_execute(
  File "/home/secsilm/miniconda3/lib/python3.11/site-packages/sqlalchemy/engine/default.py", line 924, in do_execute
    cursor.execute(statement, parameters)
  File "/home/secsilm/miniconda3/lib/python3.11/site-packages/pymysql/cursors.py", line 153, in execute
    result = self._query(query)
             ^^^^^^^^^^^^^^^^^^
  File "/home/secsilm/miniconda3/lib/python3.11/site-packages/pymysql/cursors.py", line 322, in _query
    conn.query(q)
  File "/home/secsilm/miniconda3/lib/python3.11/site-packages/pymysql/connections.py", line 558, in query
    self._affected_rows = self._read_query_result(unbuffered=unbuffered)
                          ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/secsilm/miniconda3/lib/python3.11/site-packages/pymysql/connections.py", line 822, in _read_query_result
    result.read()
  File "/home/secsilm/miniconda3/lib/python3.11/site-packages/pymysql/connections.py", line 1200, in read
    first_packet = self.connection._read_packet()
                   ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/secsilm/miniconda3/lib/python3.11/site-packages/pymysql/connections.py", line 772, in _read_packet
    packet.raise_for_error()
  File "/home/secsilm/miniconda3/lib/python3.11/site-packages/pymysql/protocol.py", line 221, in raise_for_error
    err.raise_mysql_exception(self._data)
  File "/home/secsilm/miniconda3/lib/python3.11/site-packages/pymysql/err.py", line 143, in raise_mysql_exception
    raise errorclass(errno, errval)
sqlalchemy.exc.ProgrammingError: (pymysql.err.ProgrammingError) (1064, "You have an error in your SQL syntax; check the manual that corresponds to your MySQL server version for the right syntax to use near '%s' at line 1")
[SQL: SELECT * FROM `news_detail_202505` WHERE `news_id`=%%s]
(Background on this error at: https://sqlalche.me/e/20/f405)
```

报错很长，但主要是两个报错：

- `(2006, "MySQL server has gone away (BrokenPipeError(32, 'Broken pipe'))")`
- `(1064, "You have an error in your SQL syntax; check the manual that corresponds to your MySQL server version for the right syntax to use near '%s' at line 1")`

但是很明显 root cause 是前者，意味着连接丢失了。

这是因为 MySQL 默认会自动断开空闲太久的连接，默认为 8 小时，你可以使用如下命令查看你的相应设置：

```sql
SHOW VARIABLES LIKE 'wait_timeout';
```

sqlalchemy 有自动回收旧连接（`pool_recycle`）和每次使用连接前先 ping 检查是否活跃（`pool_pre_ping`）的机制。默认情况下，`pool_recycle = -1`，即不会自动回收，`pool_pre_ping` 也是 `False`。

我们可以将回收时间设为 7 小时，打开 pre ping，这样就可以保持连接活跃，避免上述错误。当一个连接空闲超过 7 小时，该连接就会被 close 然后新建一个连接。

但是有一点需要注意，如果你单独设置 pre ping 而不设置 recycle，那么每次使用连接前，都会先 ping，执行类似 [`SELECT 1`](https://docs.sqlalchemy.org/en/20/core/pooling.html#dealing-with-disconnects) 的操作，会有一定的耗时（虽然极低）。那为什么结合 recycle 就不会每次都调用呢？根据 ChatGPT 4o（我未查证），这是因为：

> SQLAlchemy 在连接池中记录了每个连接的创建时间。每次取出连接时，会比较：
> 
> ```
> time_now - creation_time < pool_recycle
> ```
>
> 如果仍在生命周期内（即“新鲜”），就直接用，不会触发 pre_ping。
