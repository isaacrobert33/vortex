import subprocess
import threading
import os

p = subprocess.Popen(
    ["bash"],
    stderr=subprocess.PIPE,
    shell=False,
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
)
exit = False
HOME_DIR = os.path.expanduser("~")


def read_stdout():
    while not exit:
        msg = p.stdout.readline()
        print(msg.decode())


def read_stderro():
    while not exit:
        msg = p.stderr.readline()
        print("stderr: ", msg.decode())


threading.Thread(target=read_stdout).start()
threading.Thread(target=read_stderro).start()

while not exit:
    res = input(f"{os.getcwd()}$ ".replace(HOME_DIR, "~"))

    if "cd " in res:
        s = res.split(" ")
        os.chdir(s[s.index("cd") + 1])

    elif "exit" in res:
        exit = True

    p.stdin.write((res + "\n").encode())
    p.stdin.flush()
