# 格式化硬盘为 exfat

我有一个 NTFS 格式的移动硬盘。我想在 Mac 上使用，但是 Mac 上只能读而不能写，除非使用第三方工具，比如 Paragon 的 [‎Microsoft NTFS for Mac](https://www.paragon-software.com/home/ntfs-mac/)，但是又比较贵（¥225），而且担心读写性能问题，所以就想一劳永逸格式化为 Windows、Linux 和 Mac 都能读写的 exfat 格式。

在使用 `rsync` 花了半小时将移动硬盘上的内容备份到一个地方后，开始格式化：

1. 安装相关库（22.04 及更高版本）：`sudo apt install exfat-fuse exfatprogs`。
2. 找到硬盘 id，根据你的硬盘类型和大小判断，比如我的是 1 T 的移动硬盘，那我就找大小为 900 多 GB 且 disk model 为 External USB 3.0 的硬盘：
    ```
    $ sudo fdisk -l
    Disk /dev/sda: 931.51 GiB, 1000204886016 bytes, 1953525168 sectors
    Disk model: External USB 3.0
    Units: sectors of 1 * 512 = 512 bytes
    Sector size (logical/physical): 512 bytes / 512 bytes
    I/O size (minimum/optimal): 512 bytes / 512 bytes
    Disklabel type: dos
    Disk identifier: 0x00000000
    ```
    所以我的是 /dev/sda。
3. 格式化，你可以为你的硬盘起个新名字：
    ```
    $ sudo mkfs.exfat -n {硬盘名字} /dev/sda
    exfatprogs version : 1.1.3
    Creating exFAT filesystem(/dev/sda, cluster size=131072)
    
    Writing volume boot record: done
    Writing backup volume boot record: done
    Fat table creation: done
    Allocation bitmap creation: done
    Upcase table creation: done
    Writing root directory entry: done
    Synchronizing...
    
    exFAT format complete!
    ```
    如果此时报错：`open failed : /dev/sda, Device or resource busy`，那么先 unmount（推出）硬盘，再执行上述命令。
4. 确认结果：
    ```
    # 记得先 mount。
  
    $ sudo fsck.exfat /dev/sda
    exfatprogs version : 1.1.3
    /dev/sda: clean. directories 1, files 0
  
    $ df -T | grep /dev/sda
    Filesystem     Type  1K-blocks  Used Available Use% Mounted on
    /dev/sda       exfat 976730752  1280 976729472   1% /media/alan/AlanPHD
    ```

## Reference

- [How to Format a USB Disk as exFAT on Linux](https://itsfoss.com/format-exfat-linux/)
