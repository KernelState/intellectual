import time

logs = f"logging started: {time.time_ns()}\n"

# To fix a bug with directly using logs as a string
def get_logs() -> str:
    return logs

class TextColors:
    red = "\u001b[0;31m"
    green = "\u001b[0;32m"
    yellow = "\u001b[0;33m"
    blue = "\u001b[0;34m"
    magenta = "\u001b[0;35m"
    cyan = "\u001b[0;36m"
    white = "\u001b[0;37m"
    underline = "\u001b[4m"
    bold = "\u001b[1m"
    inverse = "\u001b[7m"
    end = "\u001b[0m"

def print_to_log(text: str):
    logs += f"{text}\n"
    print(text)

class Logger:
    def __init__(self, prcname: str):
        self.prcname = prcname
    def log(self, msg: str, type_: str, color: str):
        print(f"{color}[{time.time_ns()} {self.prcname} {type_}] {msg}{TextColors.end}")
    def info(self, text: str):
        self.log(text, "INFO", "")
    def warn(self, text: str):
        self.log(text, "WARN", TextColors.yellow)
    def err(self, error: Exception):
        self.log(f"An error accoured {str(error)}", "ERROR", TextColors.red)
