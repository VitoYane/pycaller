# pycaller
python的启动器, 插件式开发

## 使用方法

``` python a_pycaller.py ```

会周期性自动加载并运行plugins目录下的py文件, 执行run_loop函数. 可以作为一些持久性工具的开发框架

后续可以加入:
- py文件更新, 自动重载, 重新运行
- 插件按照指定周期运行
- 插件的调试, 错误日志记录等等
