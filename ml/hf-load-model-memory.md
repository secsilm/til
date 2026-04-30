# HuggingFace Transformers 加载模型时 CPU 内存的真实占用

**⚠️ 注意：此文由 claude opus 4.7 adptive 总结生成，未经严格验证。**

## 加载方式对比

| 加载方式 | CPU RAM 峰值 | CPU RAM 最终 | VRAM 最终 |
|---|---|---|---|
| `.to("cpu")` | 1× 模型大小 | 1× 模型大小 | 0 |
| `.to("cuda")`(默认) | **~2× 模型大小** | 较低 | 1× 模型大小 |
| `device_map` + `low_cpu_mem_usage=True` | ~1 个 shard | 较低 | 1× 模型大小 |

`device_map` 只优化加载过程的**峰值**内存，不改变最终内存占用。

## 迁移：用 `device_map` 替代 `.to(device)`

```python
model = AutoModelForCausalLM.from_pretrained(
    "model-name",
    device_map=device,           # 支持 str / int / dict
    low_cpu_mem_usage=True,
)
```

`device_map={"": "cuda"}` 的空字符串 key 表示"所有未指定的层"，等价于 `device_map="cuda"`。

## 反直觉：小模型加载到 GPU，host RAM 反而更高

实测 BERT 类小模型，GPU 加载的进程 host memory 比 CPU 加载更高。原因是 GPU 加载有一笔**固定开销**：

- **CUDA runtime 库**（libcudart / libcublas / libcudnn）≈ 500–1000 MiB
- **CUDA context + pinned memory** ≈ 100 MiB
- **Python 对象图、mmap 的 safetensors** 仍占 RAM

```
省下来的 = 模型权重大小（小模型只有几百 MiB）
新增的   = CUDA 固定开销（~600 MiB，与模型大小无关）
```

临界点示例：

```
400 MiB BERT:  CPU 加载 ~1.1 GiB  vs  GPU 加载 ~1.3 GiB  ← 反而更高
14 GiB 7B:     CPU 加载 ~14.7 GiB vs  GPU 加载 ~1.7 GiB  ← 优势明显
```

只有当**模型权重 >> CUDA 固定开销**时，GPU 加载省 host RAM 才成立。

## 真正降低内存：量化

```python
from transformers import BitsAndBytesConfig

model = AutoModelForCausalLM.from_pretrained(
    "model-name",
    device_map="auto",
    quantization_config=BitsAndBytesConfig(load_in_4bit=True),  # ~4× 压缩
)
```

或至少用 `torch_dtype=torch.float16` / `torch.bfloat16` 减半。

## 相关知识点

- **`.half()` == `torch.float16`**，只是简写；同理 `.float()` / `.double()` / `.bfloat16()`
- **BF16 = Brain Float 16**（Google Brain 提出）：和 FP32 同样 8 位指数，mantissa 只有 7 位 → range 大不易溢出，但精度低；FP16 反过来，精度高但训练易 NaN
- **BF16 硬件支持**：Ampere+（RTX 30xx / A100）、Hopper、TPU、Apple Silicon 支持；Turing（RTX 20xx / T4）、Volta（V100）**不支持**
- **DeBERTa 在 FP16 下可能不稳定**，优先用 BF16
- 运行时检测：`torch.cuda.is_bf16_supported()`
