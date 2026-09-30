import tkinter as tk
from datetime import datetime, timedelta

DURATION_MINUTES = 30

root = tk.Tk()
root.title("Security Awareness Training")
root.configure(bg="#9b0000")
root.attributes("-fullscreen", True)
root.attributes("-topmost", True)

end_time = datetime.now() + timedelta(minutes=DURATION_MINUTES)

title = tk.Label(
    root,
    text="SECURITY AWARENESS TRAINING",
    font=("Arial", 34, "bold"),
    fg="white",
    bg="#9b0000"
)
title.pack(pady=(60, 10))

simulation = tk.Label(
    root,
    text="SIMULATION ONLY — NO FILES HAVE BEEN ENCRYPTED",
    font=("Arial", 20, "bold"),
    fg="yellow",
    bg="#9b0000"
)
simulation.pack(pady=10)

warning = tk.Label(
    root,
    text="YOUR SYSTEM HAS BEEN LOCKED",
    font=("Arial", 48, "bold"),
    fg="white",
    bg="#9b0000"
)
warning.pack(pady=(45, 25))

message = tk.Label(
    root,
    text=(
        "This is a cybersecurity awareness simulation.\n\n"
        "In a real ransomware incident, files may become inaccessible,\n"
        "business operations may be interrupted, and sensitive data may be at risk.\n\n"
        "Never open unknown attachments or execute untrusted files.\n"
        "Report suspicious activity to your security team immediately."
    ),
    font=("Arial", 19),
    fg="white",
    bg="#9b0000",
    justify="center"
)
message.pack(pady=20)

countdown_title = tk.Label(
    root,
    text="SIMULATION TIMER",
    font=("Arial", 18, "bold"),
    fg="white",
    bg="#9b0000"
)
countdown_title.pack(pady=(30, 5))

countdown = tk.Label(
    root,
    text="",
    font=("Courier", 52, "bold"),
    fg="yellow",
    bg="#9b0000"
)
countdown.pack()

info = tk.Label(
    root,
    text="Press ESC to exit the training simulation.",
    font=("Arial", 16),
    fg="white",
    bg="#9b0000"
)
info.pack(side="bottom", pady=40)

def update_timer():
    remaining = end_time - datetime.now()

    if remaining.total_seconds() <= 0:
        countdown.config(text="00:00:00")
        return

    seconds = int(remaining.total_seconds())
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60

    countdown.config(
        text=f"{hours:02d}:{minutes:02d}:{secs:02d}"
    )

    root.after(1000, update_timer)

root.bind("<Escape>", lambda event: root.destroy())

update_timer()
root.mainloop()
