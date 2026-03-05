from time import strftime

FILE_NAME_LOG = f"log_{strftime('%d.%m.%y_%H.%M')}.txt"
FILE_NAME_EXCEL = f"excel_{strftime('%d.%m.%y_%H.%M')}.xlsx"
FILE_NAME_RESUME = f"resume_{strftime('%d.%m.%y_%H.%M')}"

def log( message, level="INFO"):
    with open(f"log/{FILE_NAME_LOG}", "a", encoding="utf-8") as log_file: 
        log_file.write(f"[{strftime('%H:%M:%S')}] {level.upper()}: {message}\n")
