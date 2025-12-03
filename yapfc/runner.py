import subprocess

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

