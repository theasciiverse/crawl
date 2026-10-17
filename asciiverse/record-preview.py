#!/usr/bin/env python3
"""Records asciiverse/crawl.cast, the catalog preview of Dungeon Crawl Stone
Soup, at 100x30 (hub/RECORDING.md): a Minotaur Fighter called Ada, on a
fixed seed, explores the first floor with autoexplore (o), fights what she
meets with autofight (Tab), and saves and quits (Ctrl-S) at the end.
Usage, from the repo root after asciiverse/build.sh:
    python3 asciiverse/record-preview.py [seed]"""
import os, pty, select, shutil, signal, struct, sys, fcntl, tempfile, termios, time

root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
seed = sys.argv[1] if len(sys.argv) > 1 else "7"
stage = tempfile.mkdtemp()
shutil.copytree(f"{root}/out/crawl", f"{stage}/crawl")
home = f"{stage}/home"
os.mkdir(home)
env = {"HOME": home, "USER": "player", "LOGNAME": "player", "PATH": "/usr/bin:/bin",
       "TERM": "xterm-256color", "COLORTERM": "truecolor", "LANG": "C.UTF-8"}
TAB = b"\t"
# explore and fight anything in reach; Escape closes any prompt before the
# save and quit
play = [b"o", TAB, TAB] * 19
keys = [(1.5, b"c"), (2.0, b"")] + [(0.7, k) for k in play] + [(2.0, b"\x1b"), (1.5, b"\x13"), (2.0, b"")]

def spawn(argv):
    pid, fd = pty.fork()
    if pid == 0:
        os.chdir(f"{stage}/crawl")
        os.execvpe(argv[0], argv, env)
    fcntl.ioctl(fd, termios.TIOCSWINSZ, struct.pack("HHHH", 30, 100, 0, 0))
    return pid, fd

def pump(fd, wait, until=None):
    """reads the screen for wait seconds, or until the bytes `until` show"""
    seen, end = b"", time.time() + wait
    while time.time() < end:
        r, _, _ = select.select([fd], [], [], 0.05)
        if r:
            try: seen += os.read(fd, 65536)
            except OSError: break
            if until and until in seen: return True
    return False

game = ["./crawl", "-name", "Ada", "-species", "Minotaur", "-background", "Fighter", "-seed", seed]
# a first run builds crawl's level and text caches in the data folder, which
# takes several seconds; do it before recording, then stop that run
pid, fd = spawn(game)
pump(fd, 120, b"choice of weapons")
os.kill(pid, signal.SIGKILL)
os.waitpid(pid, 0)
os.close(fd)

pid, fd = spawn(["asciinema", "rec", "--overwrite", "-q", "-i", "2",
    "--title", "Dungeon Crawl Stone Soup", "--capture-env", "TERM,COLORTERM,LANG",
    "-c", " ".join(game), f"{root}/asciiverse/crawl.cast"])
pump(fd, 30, b"choice of weapons")
for wait, key in keys:
    pump(fd, wait)
    if key: os.write(fd, key)
deadline = time.time() + 15
while time.time() < deadline:
    r, _, _ = select.select([fd], [], [], 0.2)
    if r:
        try:
            if not os.read(fd, 65536): break
        except OSError: break
    if os.waitpid(pid, os.WNOHANG)[0]: break
shutil.rmtree(stage, ignore_errors=True)
