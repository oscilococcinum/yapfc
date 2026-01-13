import json
import subprocess
import time
import functools
import numpy as np


def timeit(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        elapsed = time.perf_counter() - start
        print(f"{func.__name__} took {elapsed:.6f} s")
        return result
    return wrapper

def save_inp_file(inp_text, inp_name) -> None:
    with open(f"{inp_name}.inp", 'w') as file:
        file.writelines(inp_text)

def run_script(ccx_path: str, inp_name: str) -> None:
    try:
        process = subprocess.Popen(
            [f"{ccx_path}", inp_name, "-o", "exo"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            shell=False
        )
        print("Script output:", process.stdout)
    except Exception as e:
        print("Error starting CalculiX script:", str(e))

def open_paraview(paraview_path, result_file_path: str) -> None:
    try:
        process = subprocess.Popen(
            [f"{paraview_path}", result_file_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            shell=False
        )
        print("ParaView launched successfully.")
    except Exception as e:
        print("Error launching ParaView:", str(e))

def listToText(l: list[str]):
    text: str = ''
    for line in l:
        text += line
    return text

def getFieldFromJson(json_file:str, field:str) -> str:
        try:
            with open(f"{json_file}", "r") as f:
                options = json.load(f)
                return options.get(f"{field}", "")
        except:
            raise FileNotFoundError
