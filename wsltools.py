import os
import platform
from os.path import join

WIN_MOUNT = r"C:\Users"
UNIX_MOUNT = "~/"
WSL_MOUNT = "/mnt/c/Users/"

mount = ""
wsl_user = ""
mode = "DEFAULT"

def start():
    global mode
    mode = "WSL"

def exit():
    global mode
    mode = "DEFAULT"
    __select_sys()

def __select_sys():
    global mount
    sys = platform.system()
    if sys == "Linux" or sys == "Darwin":
        mount = UNIX_MOUNT
    elif sys == "Windows":
        mount = WIN_MOUNT
    
def set_wsl_user(user):
    global wsl_user
    if not os.path.isdir(join(WSL_MOUNT, user)):
        raise SystemError(f"The path '{WSL_MOUNT}{user}' is not a valid user.")
    wsl_user = user

def list_dir(path):
    global wsl_user
    if wsl_user:
        wsl_path = join(WSL_MOUNT, wsl_user, path)
        return os.listdir(wsl_path)

    wsl_path = join(WSL_MOUNT, path)
    return os.listdir(wsl_path)

def move_file():
    pass 

def move_dir():
    pass

__select_sys()
