__author__ = "Alexandre - Léo - Maxime"

import os

def run_python_file(file_path):
    if os.name == 'nt':
        os.system(f'start cmd /k py {file_path}')
    else:
        os.system(f'gnome-terminal -e "python {file_path}"' )

file1 = "rpyc-server.py"
file2 = "flask-server.py"

run_python_file(file1)
run_python_file(file2)
