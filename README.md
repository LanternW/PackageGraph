
## PackageGraph

这是一个小工具，用于构建ROS工程时，可视化各功能包的依赖图，辅助解决构建过程中出现的组织/编译错误。


## 使用方法：

假设你的ros工程的目录是：

    catkin_ws/
       ├── build/
       ├── devel/
       └── src/
             ├── ...

首先将仓库克隆到catkin_ws目录下
```
cd catkin_ws
git clone https://github.com/LanternW/PackageGraph.git
```
现在工作目录应当是这样：

     catkin_ws/
       ├── PackageGraph/
       ├── build/
       ├── devel/
       └── src/
             ├── ...

然后
```
cd PackageGraph
./run
```

## 功能：

1. Scan ：扫描工程的依赖关系，检查循环依赖，出现循环依赖的节点将被红色标记。
2. Show Custom Packages： 仅显示自定义功能包。
3. Show All Packages： 显示所有功能包。
4. Show Include Graph： 显示引用图。如果编译出现No such file error 可以看看引用图中是否有红色节点。
5. Layer：切换布局模式 层级布局/弹簧力模型布局

双边框的节点是自定义功能包。

左键拖拽，滚轮缩放。

鼠标移动到节点上时，橙色是依赖的包（上游），绿色是依赖此节点的包（下游）

鼠标移动到节点上时，点击左键显示该功能包可执行文件中的头文件引用列表，可作为实际依赖参考。

鼠标移动到节点上时，点击中键打开 CMakeLists.txt

鼠标移动到节点上时，点击右键可尝试搜索两个包之间是否成功构建依赖。搜索是有方向性的，假设检查
packageA是否成功依赖PCL，点击顺序是PCL -> packageA。右键空白位置取消。

调整 PackageGraph/config/default.json中的 "theme" 字段 (1~7整数)， 可以更换界面主题。



