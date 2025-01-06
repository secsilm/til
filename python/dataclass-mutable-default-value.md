# 在 dataclass 中设置 mutable 类型的默认值

在 python 中，使用可变对象（mutable）作为默认值相当危险，因为它是**可变的**，看下面的例子：

```python
class MyClass:
    my_list: list = []

# Creating two instances
obj1 = MyClass()
obj2 = MyClass()

# Modifying obj1's list
obj1.my_list.append(1)

# Both instances will have the modified list
print(obj1.my_list)  # Output: [1]
print(obj2.my_list)  # Output: [1]  # <-- obj2 的 my_list 也被改变了。
```

所以在 `dataclass` 中，设置 mutable 类型数据作为默认值是不合法的，会直接报错：

```python
from dataclasses import dataclass

@dataclass
class MyClass:
    my_list: list = []

# Creating two instances
obj1 = MyClass()
obj2 = MyClass()

# Modifying obj1's list
obj1.my_list.append(1)

# Both instances will have the modified list
print(obj1.my_list)
print(obj2.my_list)
```

上述代码只是在前面的例子上将 `MyClass` 变成了一个 `dataclass`。运行时会直接报错：

```python
ValueError: mutable default <class 'list'> for field my_list is not allowed: use default_factory
```

那么如何避免这个错误，同时又可以将可变对象作为默认值呢？使用 `field` 和 `default_factory`：

```python
from dataclasses import dataclass, field

@dataclass
class MyClass:
    my_list: list = field(default_factory=list)  # <-- 只改变了这里

# Creating two instances
obj1 = MyClass()
obj2 = MyClass()

# Modifying obj1's list
obj1.my_list.append(1)

# Both instances will have the modified list
print(obj1.my_list)  # Output: [1]
print(obj2.my_list)  # Output: []  <-- obj2 未被影响。
```
