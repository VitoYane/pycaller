
from time import strftime, sleep
import b_common as f

RUNTIME = 0
    
def run_loop():
    global RUNTIME
    RUNTIME += 1; t = len(f.get_value('Thread', []))
    # if RUNTIME > 1: return
    f.rprint(f"[{strftime('%Y-%m-%d %H:%M:%S')}] -> [{__file__}] [RunCount: {RUNTIME:4}] [ThreadCount: {t}]")
    try:
        sleep(2)
    
    except Exception as e:
        f.console.print_exception(show_locals=True)
    
    