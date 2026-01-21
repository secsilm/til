# 重命名 git 远程分支

说是重命名，实际上是替换。

假如你或你公司所用的 git 不支持在网页上重命名或新建分支，然后我们错误地推送了一个分支，比如期望是 master，但是不小心推了 main。那么可以参照以下步骤，使远程只有 master 分支。

1. 本地新建 master 分支：`git checkout -b master`。    
2. 推送到远程：`git push -u origin master`。
3. 删除远程 main：`git push origin --delete main`。
4. 删除本地 main：`git branch -d main`。

如果你使用的是 github，那么直接在网页上重命名即可。
