import os
import platform
from os.path import join

WIN_MOUNT = r"C:\Users"
UNIX_MOUNT = "~/"
WSL_MOUNT = "/mnt/"

mount = ""
wsl_user = ""
mode = "DEFAULT"

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

def resolve_path(path: str, check: bool = False) -> str:
    if mode == "DEFAULT":
        return path
    
    # Second char is always gonna be a ":" as in C:/users/johndoe (in windows)
    if path[1] != ":": 
        raise ValueError("This is not an absolute path string!")
    
    treated = path.replace(":", "")
    treated = treated.replace("\\", "/")
    # The driver's letter name must be lower case for it to work
    treated = treated.replace(treated[0], treated[0].lower(), 1)
    treated = join(WSL_MOUNT, treated)

    if not check:
        return treated 
    
    if os.path.isdir(treated) or os.path.isfile(treated):
        return treated
    else: 
        raise ValueError("This path doesn't exist!")

def move_file():
    pass 

def move_dir():
    pass

def __select_sys():
    global mount, mode
    sys = platform.system()
    if sys == "Linux" or sys == "Darwin":
        mount = UNIX_MOUNT
        mode = "WSL"
    elif sys == "Windows":
        mount = WIN_MOUNT
        mode = "DEFAULT"

__select_sys()
