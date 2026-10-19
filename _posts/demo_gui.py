from pathlib import Path
from datetime import datetime, timedelta
import subprocess
import tkinter as tk
from tkinter import messagebox
from lab_crypto import BASE, SOURCE, encrypt_copies, recover_copies

BG = '#8b0000'
root = tk.Tk()
root.title('UNT Security Awareness Lab')
root.configure(bg=BG)
w = min(860, root.winfo_screenwidth() - 60)
h = min(600, root.winfo_screenheight() - 80)
root.geometry(f'{w}x{h}+{(root.winfo_screenwidth()-w)//2}+{(root.winfo_screenheight()-h)//2}')
root.bind('<Escape>', lambda event: root.destroy())
root.grid_columnconfigure(0, weight=1)
root.grid_rowconfigure(0, weight=1)
main = tk.Frame(root, bg=BG)
main.grid(row=0, column=0, padx=15, pady=10)

try:
    from PIL import Image, ImageTk
    logo = Path(__file__).with_name('unt_mascot.png')
    img = Image.open(logo).convert('RGBA')
    img.thumbnail((180, 280))
    image = ImageTk.PhotoImage(img)
    mascot = tk.Label(main, image=image, bg=BG)
    mascot.image = image
    mascot.grid(row=0, column=0, padx=12)
except Exception:
    tk.Label(main, text='UNT', bg=BG, fg='white', font=('Arial', 40, 'bold')).grid(row=0, column=0, padx=12)

right = tk.Frame(main, bg=BG)
right.grid(row=0, column=1, padx=5)

def label(value, size=12, color='white'):
    widget = tk.Label(right, text=value, bg=BG, fg=color, font=('Arial', size, 'bold'), wraplength=440)
    widget.pack(pady=7)
    return widget

label('RANSOMWARE SIMULATION', 24)
label('BACKUP-FIRST PDF ENCRYPTION LAB', 14, '#ffe600')
label('Only PDF copies are encrypted. Originals stay available.', 10)
timer = tk.Label(right, text='00:30:00', fg='#ffe600', bg='#171717', font=('Courier', 32, 'bold'), padx=20, pady=10)
timer.pack(pady=10)
end = datetime.now() + timedelta(minutes=30)

def tick():
    remaining = max(0, int((end - datetime.now()).total_seconds()))
    timer.config(text=f'{remaining//3600:02}:{remaining//60%60:02}:{remaining%60:02}')
    if remaining:
        root.after(1000, tick)

tick()
status = label('Ready to start local training', 11, '#ffe600')

def encrypt():
    if not messagebox.askyesno('Training confirmation', 'Back up PDFs and create .unt encrypted copies inside critical_tk0667? Originals will remain unchanged.'):
        return
    try:
        count = encrypt_copies()
        status.config(text=f'{count} encrypted copies created')
    except Exception as exc:
        status.config(text='Encryption failed: ' + str(exc)[:100])

tk.Button(right, text='ENCRYPT PDF COPIES', command=encrypt, padx=15, pady=6).pack(pady=7)
tk.Button(right, text='VIEW TEST FILES', command=lambda: subprocess.Popen(['xdg-open', str(SOURCE)])).pack(pady=5)
label('4-DIGIT DEMO RECOVERY CODE', 11)
entry = tk.Entry(right, width=13, font=('Arial', 18), justify='center', show='*')
entry.pack(pady=4)

def recover():
    try:
        expected = (BASE / 'recovery_code.txt').read_text(encoding='utf-8').strip()
        if len(expected) != 4 or not expected.isdigit() or entry.get().strip() != expected:
            status.config(text='INVALID RECOVERY CODE')
            return
        count = recover_copies()
        status.config(text=f'{count} PDFs recovered and verified')
        subprocess.Popen(['xdg-open', str(BASE / 'recovered_output')])
    except Exception as exc:
        status.config(text='Recovery failed: ' + str(exc)[:100])

tk.Button(right, text='RECOVER AND VERIFY COPIES', command=recover, padx=14, pady=6).pack(pady=7)
label('SIMULATION ONLY  •  ESC = Exit', 10)
root.mainloop()
