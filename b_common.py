from loguru import logger
from sys import stdout
from os import walk, path
from re import compile, I, M
from threading import Thread
from base64 import b64encode, b64decode
from collections import defaultdict, deque
from colorama import Fore, Back, Style
from rich import print as rprint
from rich.console import Console
from rich.traceback import install
console = Console()

def _init():
    '''import的时候会初始化, 因为已经import过的不会再次import 所以过程中不用判断是否存在 _global_data_dict'''
    
    install(show_locals=True)
    global _global_data_dict
    _global_data_dict = {}

def set_value(name, value):
    '''设置值'''
    _global_data_dict[name] = value

def get_value(name, default = None):
    '''获取值'''
    try:
        return _global_data_dict[name]
    except KeyError:
        return default

def in_type_listA(data, type_list):
    return any(isinstance(data, t) for t in type_list)

def update_value(name, *args, **kwds):
    '''
    name 不存在, 将创建一个None
    name 值为字典, value 可以是字典或者元组, 更新
    name 值为列表, value 可以是列表, 也可以是其他值, 加到最后
    name 不是上述类型, 设置为value
    '''
    # 处理 args 和 kwds
    if kwds and args: 
        value = kwds.update(dict(enumerate(args)))
    elif kwds:
        value = kwds
    elif args:
        value = args[0] if len(args) == 1 else list(args)
    else:
        value = None

    # 如果没有name, 就创建一个value类型的空值
    if name not in _global_data_dict: 
        _global_data_dict[name] = type(value)()

    # 如果有name, 且值为dict类型
    if in_type_listA(_global_data_dict[name], [dict]):
        if in_type_listA(value, [dict]):
            _global_data_dict[name].update(value)
        elif in_type_listA(value, [list, set, deque]):
            _global_data_dict[name].update(dict(enumerate(value)))
        elif in_type_listA(value, [tuple]):
            if len(value) == 2:
                key, val = value
                _global_data_dict[name].update({key: val})
            else:
                _global_data_dict[name].update(dict(enumerate(value)))
    # 如果有name, 且值为列表, 集合, 元组类型
    elif in_type_listA(_global_data_dict[name], [list, set, tuple, deque]):
        _global_data_dict[name] = list(_global_data_dict[name])
        if in_type_listA(value, [list, set, tuple, deque]):
            _global_data_dict[name].extend(value)
        else:
            _global_data_dict[name].append(value)

    else:
        set_value(name, value)




def walk_dir(root_dir, ext_list = ['.txt']):
    # root_dir = f"\\\?\\{root_dir}".replace('/','\\')  # 解决长路径报错

    for root, dirs, files in walk(root_dir):
        # root 表示当前正在访问的文件夹路径
        # dirs 表示该文件夹下的子目录名list
        # files 表示该文件夹下的文件list

        # 遍历文件
        for f in files:
            if path.splitext(f)[-1] in ext_list:
                yield path.join(root, f)

        # 遍历所有的文件夹
        for d in dirs:
            walk_dir(path.join(root, d))    # 子目录


def get_all_value():
    return _global_data_dict

def update_logger(level = None):
    logger.remove()
    logger_level = str(level).upper() if level else get_value('debug', 'DEBUG').upper()
    logger.add(stdout, level = logger_level)
    logger.add('err.log', level='ERROR')

def get_err_msg(times = 1, pl = False ,_interval = ' -> '):
    '''pl=true 打印局部变量环境'''
    from sys import _getframe, exc_info
    call_str = ''; lcs = ''; _frame = _getframe(); n = -1
    while _frame and n <= times:
        No = _frame.f_lineno
        cname = _frame.f_code.co_name
        if call_str == '':call_str = '|'
        else:
            if lcs == '':
                for k, v in _frame.f_locals.items():
                    lcs = f'{lcs}\t{repr(k):20.20s}: {repr(v):100.100s}\n'
                lcs = f'\n{lcs}'
                No = exc_info()[2].tb_lineno if exc_info()[2] != None else None
            call_str = f'{cname}({No}){_interval}{call_str}'
        _frame = _frame.f_back; n += 1
    return f"\n{call_str[:-len(_interval)]}: {exc_info()[1]} {exc_info()[0]}\n{lcs}\n{'-' * 79}\n\n" if pl else f"{call_str[:-len(_interval) - 1]}{_interval}{exc_info()[0]} : {exc_info()[1]}"

def get_call_link(times = 1, _interval = ' >> '):
    '''获取调用链，0是当前，1是上一个...'''
    from sys import _getframe
    call_str = ''
    _frame = _getframe(); n = -1;
    while _frame and n <= times:
        No = _frame.f_lineno
        cname = _frame.f_code.co_name
        call_str = '|' if call_str == '' else f'{cname}({No}){_interval}{call_str}'
        _frame = _frame.f_back
        n += 1
    return call_str

def cprint(*args, **kwds):
    '''kwds 中 f 设置前景色 f='red', 默认green, b 设置背景色 b='cyan', 默认black, lred表示淡红色'''
    colors = {
        'red': (Fore.RED, Back.RED),
        'green': (Fore.GREEN, Back.GREEN),
        'black': (Fore.BLACK, Back.BLACK),
        'blue': (Fore.BLUE, Back.BLUE),
        'cyan': (Fore.CYAN, Back.CYAN),
        'white': (Fore.WHITE, Back.WHITE),
        'yellow': (Fore.YELLOW, Back.YELLOW),
        'magenta': (Fore.MAGENTA, Back.MAGENTA),
        'lred': (Fore.LIGHTRED_EX, Back.LIGHTRED_EX),
        'lyellow': (Fore.LIGHTYELLOW_EX, Back.LIGHTYELLOW_EX),
        'lblue': (Fore.LIGHTBLUE_EX, Back.LIGHTBLUE_EX),
        'lcyan': (Fore.LIGHTCYAN_EX, Back.LIGHTCYAN_EX),
        'lblack': (Fore.LIGHTBLACK_EX, Back.LIGHTBLACK_EX),
        'lwhite': (Fore.LIGHTWHITE_EX, Back.LIGHTWHITE_EX),
        'lgreen': (Fore.LIGHTGREEN_EX, Back.LIGHTGREEN_EX),
        'lmagenta': (Fore.LIGHTMAGENTA_EX, Back.LIGHTMAGENTA_EX),
        'reset': (Fore.RESET, Back.RESET)
    }
    front = colors[kwds.pop('f', 'green').lower()][0]
    back = colors[kwds.pop('b', 'reset').lower()][1]
    end = kwds.pop('end', '\n')
    msg = ', '.join(args)
    
    print(f"{front}{back}{msg}{Style.RESET_ALL}", end=end, flush=1)
def findallA(patn, src_str, ret_len = 1, mode = I|M):
    '''
    使用re模块统一输出结果为[(1,2,3),(1,2,3)...], 
    能搜到多个结果统一使用句式：for r in findall('f(\d+)', a, 5): x,y,z = r; ...
    如果只想要第一个结果：x,*y =  findall('f(\d+)', a, 1)    # 这种句式是x代表第一个找到的结果，x在ret_len=1时为字符串，ret_len>1时为元组

    如果每个结果中，只有有1个提取字段，配置ret_len = 1,用下面两种方式解析
    x,*y =  findall('f(\d+)', a, 1)    # 这种句式是x代表第一个找到的结果，x在ret_len=1时为字符串，ret_len>1时为元组
    print(f"x => |{x}| {type(x)}")

    for r in findall('f(\d+)', a, 1):print(r);break

    注意需要 判断 if not r: continue 用来解决没找到的问题
    '''
    p = compile(patn, mode)
    single_list = p.findall(src_str)
    s = lambda n: tuple([''] * abs(n))
    for r in single_list:
        if isinstance(r, tuple) and len(r) == ret_len:
            yield r
        elif isinstance(r, tuple) and len(r) < ret_len:
            yield r.__add__(s(ret_len-len(r)))
        elif isinstance(r, tuple) and len(r) > ret_len:
            yield r[:ret_len]
        elif isinstance(r, str):
            if ret_len == 1 and len(r) > 0:yield r
            else:yield (r,).__add__(s(ret_len - 1))
    yield None

def err_retry(func=None, *args, **kwds):
    '''第一个参数必须是err, 本函数根据err判断重试'''
    n = kwds.pop('n', 3)
    try:
        for _ in range(n):
            ret = func(*args, **kwds)
            if in_type_listA(ret, [list, tuple]): err = ret[0] if ret else 1
            elif in_type_listA(ret, [dict]): err = ret.get('err', 1)
            else: err = ret
            if not err: break
    except Exception as e:
        logger.error(get_err_msg())
    return ret

def get_url(_str):
    ret = []
    for url_info in findallA(r'((?:http(?:s)?)+://)+((?:\d+\.\d+\.\d+\.\d+)|(?:[^/\s:]+(?:\.[^/\s:]+)+))(:\d+)?([^\s]+)?', _str, 4):
        if not url_info: continue
        schema, ip, port, path = url_info
        ret.append((f'{schema}{ip}{port}', f'{ip}{port}'))
    return ret

def str2base64(_str):
    return b64encode(_str.encode("utf-8")).decode('utf8')

def base642str(_str):
    return b64decode(_str).decode("utf-8")

def if_unique(lst):
    return len(lst) == len(set(lst))

def get_unique(lst):
    return list(set(lst))

def anyone_in_str(_list, _str):
    '''判断列表中任意一个元素在不在字符串中'''
    return any(_one in _str for _one in _list)

def str_in_anyone(_str, _list):
    '''判断字符串在不在列表中任意一个元素中'''
    return any(_str in _one for _one in _list)

def all_in_str(_list, _str):
    '''判断列表中全部元素是否都在字符串中'''
    return all(_one in _str for _one in _list)

def str_in_all(_str, _list):
    '''判断字符串在所有元素中'''
    return all(_str in _one for _one in _list)

def get_obj_attr(_obj):
    data_dict = {}
    try:
        if isinstance(_obj, dict):
            data_dict.update(_obj)

        elif isinstance(_obj, object) and "<class 'type'>" in str(_obj.__class__):    # 没有实例化的类
            for key, val in _obj.__dict__.items():
                if not str(key).startswith('_'):
                    data_dict[key] = val

        elif isinstance(_obj, object):             # 带入实例化参数
            for key in _obj.__dir__():
                if not str(key).startswith('_'): 
                    data_dict[key] = eval(f'_obj.{key}')
        return 0, data_dict

    except Exception as e:
        err_msg = get_err_msg(); logger.error(err_msg)
        return err_msg, {}

def goA(func, *args, **kwds):
    '''kwds 中 nowait, 可以设置为孤儿进程'''
    mthread=Thread(target=func, args=args, kwargs=kwds)
    mthread.daemon = kwds.pop('nowait', False)
    mthread.start()

def read_fileA(filePath, ret_type = 'list'):
    '''无错读文件，返回可选list,str '''
    from chardet import detect
    with open(filePath, 'ab+') as f:
        f.seek(0, 0); content = f.read()
        code = detect(content)['encoding']
        code = code or 'latin1'
        ret = content.decode(code, 'ignore')
        if ret_type == 'list':
            f.seek(0, 0)
            ret = list(map(lambda x: x.decode(code, 'ignore').strip(), f.readlines()))
        return ret
    
def write_file(file_name, write_data, mode = 'a+', encoding='utf-8', one_line = False, write_title = False):
    '''
    写文件，可以写字符串，元组，列表，字典等结构, 
    one_line仅对列表，集合、元组有效,
    write_title 仅对字符串有效，写标题行
    '''
    from collections import deque
    from loguru import logger
    from chardet import detect
    try:
        if write_title: mode = 'rb+'; encoding = None
        if 'b' in mode: encoding = None
        with open(file_name, mode, encoding = encoding) as fo:
            if sum(map(lambda t: isinstance(write_data, t), [str, int, float, complex])):
                if write_title:
                    content = fo.read(); co = detect(content)['encoding']
                    write_data_en = f'{write_data}\n'.encode(co or 'utf-8', 'ignore')
                    fo.seek(0,0); fo.write(write_data_en + content)
                else:
                    fo.writelines(f'{write_data}\n')
            elif sum(map(lambda t: isinstance(write_data, t), [list, tuple, deque])):
                if one_line:
                    fo.writelines(f'{write_data}\n')
                else:
                    for x in write_data:
                        fo.writelines(f'{x}\n')
            elif sum(map(lambda t: isinstance(write_data, t), [dict])):
                if one_line:
                    fo.writelines(f'{write_data}\n')
                else:
                    fo.writelines('{\n')
                    for k, v in write_data.items():
                        fo.writelines(f'\t{repr(k)} : {repr(v)},\n')
                    fo.writelines('}\n')
            else:
                logger.warning(f'未考虑的类型写入: {write_data} --> type = {type(write_data)}')
                fo.writelines(f"{str(write_data)}\n")
        return True
    except KeyboardInterrupt as e:
        logger.warning('KeyboardInterrupt')
        exit()
    except Exception as e:
        logger.exception(f'{type(e)} => {e}')
        return False
        
if __name__ != '__main__':
    _init()
    

