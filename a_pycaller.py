
from time import strftime, sleep
from os import path
from threading import enumerate
import b_common as f

myself = path.dirname(path.abspath(__file__))
done_times = 0
def run_plugins(plugins_dir = 'plugins'):
    # 遍历 [plugins] 文件夹, 遍历所有py文件导入并执行入口功能OK
    for mod in f.walk_dir(path.join(myself, plugins_dir), ['.py']):
        try:
            mod_name = str(path.basename(mod)).replace('.py', '')
            if not mod_name.startswith('__') : 
                exec(f'from {plugins_dir} import {mod_name}')
                exec(f'if "run_loop" in dir({mod_name}):f.goA({mod_name}.run_loop, nowait=True)')
        except Exception as e:
            f.logger.exception(e)
            


def main():
    global done_times
    while True:
        run_plugins('plugins')
        sleep(1)
        f.set_value('Thread', enumerate())
        if len(enumerate()) <= 1: done_times += 1
        else: done_times = 0
        if done_times > 3: f.rprint(f"\n[{strftime('%Y-%m-%d %H:%M:%S')}] -> 所有子线程结束"); break
        

if __name__ == '__main__':
    main()