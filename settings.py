from time import strftime
from pathlib import Path

TIME_FORMAT = strftime("%d.%m.%y_%H.%M.%S")
LOG_DEBUG = False 
CACHE = {}

FILES_NAMES = {
    "LOG": f"{TIME_FORMAT}.txt",
    "EXCEL": f"{TIME_FORMAT}.xlsx",
    "RESUME": f"{TIME_FORMAT}.txt"
}
DIRS = {
    "LOG": "logs",
    "DATA": "data",
    "RESUME": "resume"
}

def ensure_dirs() -> None:
    for d in DIRS.values():
        Path(d).mkdir(parents=True, exist_ok=True)

def log( message, level="INFO", txt = True) -> bool:
    print(f"[{strftime('%H:%M:%S')}] {level.upper()}: {message}")
    if level.upper() == "DEBUG" and not LOG_DEBUG or not txt:
        return False
    with open(f"{DIRS['LOG']}/{FILES_NAMES['LOG']}", "a", encoding="utf-8") as log_file: 
        if txt: log_file.write(f"[{strftime('%H:%M:%S')}] {level.upper()}: {message}\n")
    return True

def approach(*Args) -> tuple:
    log(f"Args Recebidos: {Args}", "DEBUG")
    """    
    This function can be expanded to handle different formats from various marketplaces.
    If your use that approach function, you need put the def on main_process_marketplace or
    in page_process function in store_process.py, and pass 
    the marketplace as argument, and then you can apply different approaches for each marketplace
    ===========================================================================================
    example:
    if marketplace == "Amazon":
        Args[0] = process_amazon_price(Args[0])
    ===========================================================================================
    """


    return Args
