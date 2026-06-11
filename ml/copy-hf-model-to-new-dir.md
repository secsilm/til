# 将 hf 模型复制到指定目录

1. 使用 snapshot_download 获取本地具体路径：
    ```python
    from huggingface_hub import snapshot_download
    
    snapshot_path = snapshot_download(
        repo_id="Babelscape/wikineural-multilingual-ner",
        local_files_only=True,
    )
    
    print(snapshot_path)
    
    # 输出
    # /home/username/.cache/huggingface/hub/models--Babelscape--wikineural-multilingual-ner/snapshots/bed6ee7a45d2827b6c90a4fd7983f0241ae0a5c1
    ```
2. 复制到指定目录，记得使用 `-L` 来复制真实文件而不是软链接：
   ```bash
   cp -rL /home/username/.cache/huggingface/hub/models--Babelscape--wikineural-multilingual-ner/snapshots/bed6ee7a45d2827b6c90a4fd7983f0241ae0a5c1/* /new/model/path/
   ```
