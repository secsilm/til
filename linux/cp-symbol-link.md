# cp 复制真实文件而不是 symbol link

TL;DR: `cp -L`

---

`transformers` 的默认缓存位置是 `~/.cache/huggingface`，hf 系的库缓存都是在这个位置，包括模型、datasets 和 evaluate 等。在这里我们可以找到缓存的模型文件，比如 `google/vit-base-patch16-224-in21k` 的缓存就是下面这个样子：

```
$ tree models--google--vit-base-patch16-224-in21k/
models--google--vit-base-patch16-224-in21k/
├── blobs
│   ├── 254071bbf72dd0fd535b61768d9cd87adcb776f4
│   ├── 70fbc148eb26a06bac351d46fddc0a23037b4ce4
│   └── fd4e1169c7aa6c2dbfa8a6448be13b35abc0ee256190857c90009d12c094619b
├── refs
│   └── main
└── snapshots
    └── b4569560a39a0f1af58e3ddaf17facf20ab919b0
        ├── config.json -> ../../blobs/254071bbf72dd0fd535b61768d9cd87adcb776f4
        ├── model.safetensors -> ../../blobs/fd4e1169c7aa6c2dbfa8a6448be13b35abc0ee256190857c90009d12c094619b
        └── preprocessor_config.json -> ../../blobs/70fbc148eb26a06bac351d46fddc0a23037b4ce4

4 directories, 7 files
```

可以看到 `snapshots` 中存储着模型相关文件。但如果我们直接 `cp -r b4569560a39a0f1af58e3ddaf17facf20ab919b0 new_model_dir`，那么你会发现得到的只是软链接（symbol link）文件：

```
$ ll models--google--vit-base-patch16-224-in21k/snapshots/b4569560a39a0f1af58e3ddaf17facf20ab919b0/config.json 
lrwxrwxrwx 1 jy jy 52 2月  12 16:10 models--google--vit-base-patch16-224-in21k/snapshots/b4569560a39a0f1af58e3ddaf17facf20ab919b0/config.json -> ../../blobs/254071bbf72dd0fd535b61768d9cd87adcb776f4
```

其实上面 `tree` 的命令输入已经告诉我们了这是软连接而非真实的文件，真实文件存储在 `blobs` 中。但是我想复制真实文件的同时保留原始文件名，那怎么做呢？

我们可以使用 `cp -L`：

```
$ cp -Lr b4569560a39a0f1af58e3ddaf17facf20ab919b0 new_model_dir
```

- `-L`: 全称是 `--dereference`，也就是解引用，会找到真实文件。

此外，我们可以使用 `readlink -f` 来获取真实文件的绝对路径（但不包括最后的文件名）：

```
$ readlink -f models--google--vit-base-patch16-224-in21k/snapshots/b4569560a39a0f1af58e3ddaf17facf20ab919b0/config.json 
/home/username/.cache/huggingface/hub/models--google--vit-base-patch16-224-in21k/blobs/254071bbf72dd0fd535b61768d9cd87adcb776f4
```
