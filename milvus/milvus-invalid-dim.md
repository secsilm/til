# Milvus invalid dim 错误的具体含义

Milvus search 时如果遇到 dim 不匹配，会报如下错误：

```
MilvusException: (code=65535, message=fail to search on QueryNode 14: worker(14) query failed: vector dimension mismatch, expected vector size(byte) 2048, actual 3072.)
```

注意最后的那句，看到后我自然以为期望的向量大小是 2048，但实际上拿到的是 3072，我查了好久程序。实际上我程序里传入的是一个 768 维向量，我就以为是不是我哪里写错了，传入了 3072/768=4 个向量。

结果查了好久也没查到。于是 Google，看到这个 [issue](https://github.com/milvus-io/milvus/issues/29791)，里面有个对话：

Q：

> For invalid dim:
> vector dimension mismatch, expected vector size(byte) 512, actual 516.

> Could we point out expected dim ..., actual dim...?

A：

> Suppose vector dim = 128 type = floatVector, if the query vector is 516 bytes, the actual dim is also 128, and there will be doubts. Using bytes is more accurate.

所以说注意 **vector size 后面跟的是 byte，而不是 dim**，而 milvus 默认使用 float32 存储，即 4B，所以实际上我的报错是说期望 512 维，但得到的是 768 

问题迎刃而解。
