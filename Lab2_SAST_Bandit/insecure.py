import subprocess
import hashlib
import pickle
import random
import os

password = "admin123"

command = input("Enter command: ")
subprocess.call(command, shell=True)

print(hashlib.md5(b"hello").hexdigest())

data = input("Enter serialized object: ")
pickle.loads(data.encode())

print(random.random())

os.system("ls")
