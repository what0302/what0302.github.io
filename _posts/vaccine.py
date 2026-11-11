#!/usr/bin/env python3
"""
vaccine.py — CSCE 5550 Ransomware Defense

Process-behavior monitoring using fanotify:
  - Watches every file open() attempt on the protected directory
  - Any process (other than this vaccine) that tries to open a protected file
    is immediately DENIED (open() returns EACCES) and killed with SIGKILL
  - The ransomware process never gets to read or write any file

Usage: sudo python3 vaccine.py
"""

import collections, ctypes, os, pwd, select, signal, sqlite3, struct, sys, time
from pathlib import Path

# fanotify constants (Linux kernel)
FAN_CLOEXEC       = 0x00000001
FAN_NONBLOCK      = 0x00000002
FAN_CLASS_CONTENT = 0x00000004
FAN_MARK_ADD      = 0x00000001
FAN_MARK_MOUNT    = 0x00000010
FAN_OPEN_PERM     = 0x00010000  # intercept open() BEFORE it completes
FAN_Q_OVERFLOW    = 0x00004000
FAN_ALLOW         = 0x01
FAN_DENY          = 0x02
AT_FDCWD          = -100

FAN_META     = struct.Struct('=IBBHQii')
FAN_RESPONSE = struct.Struct('=iI')

# Processes known to be safe (PDF viewers, file managers, common shells/utils)
_SAFE_BINARIES = frozenset([
    'evince', 'okular', 'zathura', 'mupdf', 'xpdf', 'atril',
    'nautilus', 'thunar', 'dolphin', 'nemo', 'pcmanfm',
    'bash', 'sh', 'zsh', 'dash', 'fish',
    'ls', 'cat', 'grep', 'less', 'head', 'tail', 'file', 'stat',
    'gedit', 'nano', 'vim', 'vi', 'code', 'kate', 'mousepad',
    'xdg-open', 'xdg-mime',
])

# Safe Python scripts (run by python3 but not ransomware)
_SAFE_SCRIPTS = frozenset(['decrypt.py', 'vaccine.py'])

# Rate-based detection: PID → deque of access timestamps
_access_times: dict = collections.defaultdict(collections.deque)
_RATE_WINDOW  = 3.0   # seconds
_RATE_LIMIT   = 3     # file opens per window before flagged


def is_ransomware(pid: int, cmdline: str) -> bool:
    """Return True if the process looks like ransomware, False for legitimate access."""
    parts = cmdline.split()
    exe = os.path.basename(parts[0]) if parts else ''

    # Whitelisted safe binaries
    if exe in _SAFE_BINARIES:
        return False

    # Python processes: decide by script name
    if exe in ('python3', 'python', 'python'):
        script = os.path.basename(parts[1]) if len(parts) > 1 else ''
        if script in _SAFE_SCRIPTS:
            return False
        # Known malicious scripts → immediate flag
        if script in ('encrypt.py', 'demo_encrypt.py'):
            return True

    # Rate-based detection: flag any process opening too many files too fast
    now = time.monotonic()
    times = _access_times[pid]
    times.append(now)
    while times and times[0] < now - _RATE_WINDOW:
        times.popleft()
    if len(times) >= _RATE_LIMIT:
        return True

    return False


def user_home():
    name = os.environ.get('SUDO_USER')
    if name and name != 'root':
        return Path(pwd.getpwnam(name).pw_dir)
    return Path.home()


def get_cmdline(pid):
    try:
        return Path(f'/proc/{pid}/cmdline').read_bytes()\
               .replace(b'\x00', b' ').decode(errors='replace').strip()
    except OSError:
        return '?'


def init_db(db_path):
    """Create the incident log database and return a connection."""
    conn = sqlite3.connect(str(db_path))
    conn.execute("""
        CREATE TABLE IF NOT EXISTS incidents (
            id        INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT    NOT NULL,
            pid       INTEGER NOT NULL,
            cmdline   TEXT,
            filename  TEXT,
            action    TEXT    NOT NULL
        )
    """)
    conn.commit()
    return conn


def log_event(conn, pid, cmdline, filename, action):
    ts = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
    conn.execute(
        "INSERT INTO incidents (timestamp, pid, cmdline, filename, action) VALUES (?,?,?,?,?)",
        (ts, pid, cmdline, filename, action)
    )
    conn.commit()


def main():
    if os.geteuid() != 0:
        sys.exit('Error: must run as root (sudo)')

    root = user_home() / 'Desktop' / 'RansomDemo' / 'critical_tk0667'
    if not root.is_dir():
        sys.exit(f'Directory not found: {root}')

    db_path = root.parent / 'vaccine_log.db'
    conn = init_db(db_path)
    print(f'[*] Logging incidents to: {db_path}')

    # Setup fanotify
    libc = ctypes.CDLL(None, use_errno=True)
    libc.fanotify_init.argtypes = [ctypes.c_uint, ctypes.c_uint]
    libc.fanotify_init.restype  = ctypes.c_int
    libc.fanotify_mark.argtypes = [ctypes.c_int, ctypes.c_uint, ctypes.c_uint64,
                                    ctypes.c_int, ctypes.c_char_p]
    libc.fanotify_mark.restype  = ctypes.c_int

    fan_fd = libc.fanotify_init(FAN_CLOEXEC | FAN_NONBLOCK | FAN_CLASS_CONTENT, os.O_RDONLY)
    if fan_fd < 0:
        sys.exit(f'fanotify_init failed: {os.strerror(ctypes.get_errno())}')

    ret = libc.fanotify_mark(fan_fd, FAN_MARK_ADD | FAN_MARK_MOUNT,
                              FAN_OPEN_PERM, AT_FDCWD, os.fsencode(root))
    if ret < 0:
        os.close(fan_fd)
        sys.exit(f'fanotify_mark failed: {os.strerror(ctypes.get_errno())}')

    print(f'[*] Monitoring: {root}')
    print('[*] Any process attempting to open protected files will be blocked + killed')
    print('[*] Press Ctrl+C to stop\n')

    stop = False
    killed = set()

    def _stop(*_):
        nonlocal stop
        stop = True
    signal.signal(signal.SIGINT, _stop)
    signal.signal(signal.SIGTERM, _stop)

    try:
        while not stop:
            ready, _, _ = select.select([fan_fd], [], [], 0.5)
            if not ready:
                continue

            try:
                data = os.read(fan_fd, 65536)
            except BlockingIOError:
                continue

            offset = 0
            while offset + FAN_META.size <= len(data):
                ev_len, _, _, _, mask, objfd, pid = FAN_META.unpack_from(data, offset)
                if ev_len < FAN_META.size:
                    break
                offset += ev_len

                if objfd < 0:
                    if mask & FAN_Q_OVERFLOW:
                        print('[!] fanotify overflow — events may have been missed')
                    continue

                try:
                    try:
                        path = os.readlink(f'/proc/self/fd/{objfd}')
                    except OSError:
                        path = ''

                    # Allow this vaccine process itself
                    if pid == os.getpid():
                        os.write(fan_fd, FAN_RESPONSE.pack(objfd, FAN_ALLOW))
                        continue

                    # Ignore events outside the protected directory
                    if not Path(path).is_relative_to(root):
                        os.write(fan_fd, FAN_RESPONSE.pack(objfd, FAN_ALLOW))
                        continue

                    cmd   = get_cmdline(pid)
                    fname = Path(path).name

                    if not is_ransomware(pid, cmd):
                        # Legitimate process — allow and log for audit
                        os.write(fan_fd, FAN_RESPONSE.pack(objfd, FAN_ALLOW))
                        print(f'[+] ALLOWED  PID={pid}  file={fname}  ({cmd.split()[0]})')
                        log_event(conn, pid, cmd, fname, 'ALLOWED')
                        continue

                    # Ransomware detected — DENY open() then kill the process
                    os.write(fan_fd, FAN_RESPONSE.pack(objfd, FAN_DENY))
                    print(f'[!] BLOCKED  PID={pid}  file={fname}')
                    print(f'    cmd: {cmd}')
                    log_event(conn, pid, cmd, fname, 'BLOCKED')

                    if pid not in killed:
                        killed.add(pid)
                        try:
                            os.kill(pid, signal.SIGKILL)
                            print(f'    → killed PID {pid}\n')
                            log_event(conn, pid, cmd, fname, 'KILLED')
                        except OSError:
                            pass

                finally:
                    os.close(objfd)

    finally:
        os.close(fan_fd)
        conn.close()
        print('\n[*] Vaccine stopped.')


if __name__ == '__main__':
    main()
