# Linux-Lab

A hands-on Linux practice lab with runnable scripts covering files, permissions, processes, networking, archiving, logs, and more.

> **IMPORTANT:** This repo is meant to be cloned into Ubuntu and run there. Scripts will not work on Windows.

---

## Setup (after cloning into Ubuntu)

> `~/` is a shortcut for your home directory — e.g., `/home/vboxuser` on Ubuntu.

```bash
mkdir -p ~/projects
cd ~/projects
git clone https://github.com/GasimV/Self-Study-Tech-Projects
cd Self-Study-Tech-Projects/Linux-Lab
chmod +x lab/*.sh scripts/*.sh
```

> **Why `chmod +x`?**
> On Linux, every file has three permission bits: **read (r)**, **write (w)**, **execute (x)**.
> A `.sh` file is just a text file — without the `x` bit, Linux refuses to run it as a program:
>
> ```
> ./lab/01-files.sh   # → Permission denied ✗
> ```
>
> `chmod +x` adds the execute bit so the OS treats it as a runnable script:
>
> ```
> chmod +x lab/*.sh   # add execute to all .sh files in lab/
> ./lab/01-files.sh   # → works ✓
> ```
>
> **Why it's needed after cloning:** Git on Windows doesn't preserve Linux file permissions.
> When you push from Windows and clone on Ubuntu, all `.sh` files arrive without the execute bit. `chmod +x` restores it.
>
> You can always bypass it with `bash script.sh`, but `chmod +x` is the correct Linux way — and it's exactly what `lab/02-permissions.sh` teaches you.

---

## Running Lab Scripts

Each script is self-contained. Run from the repo root:

```bash
bash lab/01-files.sh        # mkdir, cp, mv, ls practice
bash lab/02-permissions.sh  # chmod examples
bash lab/03-search.sh       # grep and find
bash lab/04-processes.sh    # ps and pgrep
bash lab/05-network.sh      # ip, ping, curl
bash lab/06-archive.sh      # tar create and list
bash lab/07-backup.sh       # timestamped backup
bash lab/08-logs.sh         # head, tail, grep on logs
bash lab/09-env.sh          # export and env vars
bash lab/10-cleanup.sh      # clean data/output/
```

---

## Reading `ip a` Output

Each block = one network interface. Scan for `enp*` lines and look for `inet`.

| Interface  | Example IP       | What it is                        |
|------------|------------------|-----------------------------------|
| `lo`       | `127.0.0.1`      | Loopback — self only, ignore      |
| `enp0s3`   | `10.0.2.15`      | Internet (VirtualBox NAT)         |
| `enp0s8`   | `192.168.56.x`   | Host ↔ VM (SSH, file transfer)    |
| `flannel.1`| `10.244.0.x`     | Kubernetes overlay network        |
| `cni0`     | `10.244.0.1`     | Container bridge (K8s/Docker)     |
| `veth*`    | no IP            | Virtual cables to containers      |

**What to use in this lab:**
- `enp0s3` — internet access (`ping`, `curl`, `apt`)
- `enp0s8` — connect from Windows host (`ssh`, `scp`)

---

## Script Header Explained

Every script in this repo starts with:

```bash
#!/usr/bin/env bash
set -euo pipefail
```

| Line                  | What it does                                   |
|-----------------------|------------------------------------------------|
| `#!/usr/bin/env bash` | Run this script with Bash                      |
| `set -e`              | Exit immediately if any command fails          |
| `set -u`              | Error if an undefined variable is used         |
| `set -o pipefail`     | Fail if any command in a pipeline fails        |

> "Run with Bash + fail fast + no silent errors"

---

## Script Portability Pattern

Every script in this repo starts with:

```bash
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
```

**What it does:**

| Variable     | Value (example)               | Meaning              |
|--------------|-------------------------------|----------------------|
| `SCRIPT_DIR` | `/home/user/Linux-Lab/scripts`| Where the script is  |
| `REPO_ROOT`  | `/home/user/Linux-Lab`        | Project root         |

**Why it matters** — without it, relative paths break when you run the script from a different directory:

```bash
cp data/input/file.txt data/backup/   # breaks if run from outside the repo
cp "$REPO_ROOT/data/input/file.txt" "$REPO_ROOT/data/backup/"  # always works
```

**How it works:**

- `${BASH_SOURCE[0]}` — path of the current script (e.g., `/home/user/Linux-Lab/scripts/backup.sh`)
- `dirname` — strips the filename, leaving the directory (e.g., `/home/user/Linux-Lab/scripts`)
- `cd ... && pwd` — resolves it to an absolute path (`pwd` = **P**rint **W**orking **D**irectory)
- `$SCRIPT_DIR/..` — goes one level up to the repo root (e.g., `/home/user/Linux-Lab`)

**Under the hood (very short):**

* Bash → handles variables + `$(...)`; it is the **brain**
* `dirname`, `pwd` → normal programs; **tools**
* Linux kernel → executes commands + handles filesystem; **executor**
* **One-Line Mental Model**: Bash orchestrates everything, external tools do small jobs, and the Linux kernel executes the actual system operations.

> This pattern makes scripts location-independent — run them from anywhere.

---

## Using Reusable Scripts

```bash
bash scripts/hello.sh           # print user, host, directory
bash scripts/backup.sh          # backup data/input → data/backup
bash scripts/monitor_python.sh  # check for running python processes
bash scripts/show_ip.sh         # show IP addresses
```

Source `scripts/common.sh` in your own scripts for logging helpers:

```bash
source scripts/common.sh
log_info  "Starting task"
log_warn  "Something looks off"
log_error "Something failed"
```


---

## systemd User Service

The service writes a timestamp every 10 seconds to `data/output/linux-lab-service.log`.

```bash
# 1. Copy the unit file to your user systemd directory
mkdir -p ~/.config/systemd/user
cp services/linux-lab.service ~/.config/systemd/user/

# Edit the ExecStart line — replace %h with your actual home path if needed
# Default %h expands to $HOME automatically in systemd

# 2. Reload and control
# daemon-reload: makes systemd read new/updated .service files
# Required after adding or editing a service — systemd won't auto-detect changes
systemctl --user daemon-reload
systemctl --user start linux-lab
systemctl --user status linux-lab
systemctl --user stop linux-lab
systemctl --user restart linux-lab

# 3. Follow logs
journalctl --user -u linux-lab -f
```

**`--user` vs system:**

| Flag       | Talks to              | Service files                  | Needs sudo? |
|------------|-----------------------|--------------------------------|-------------|
| `--user`   | Your user systemd     | `~/.config/systemd/user/`      | No          |
| *(none)*   | System-wide systemd   | `/etc/systemd/system/`         | Yes         |

**`daemon-reload`** — tells systemd to re-read all unit files from disk and rebuild its internal state (updates dependency graph). Run it every time you add or edit a `.service` file.

> `--user` selects your personal systemd instance; `daemon-reload` makes it re-read service files from disk.

---

## Cron Job

**cron** = background scheduler. **crontab** = your personal list of scheduled commands.

Runs `backup.sh` every 5 minutes.

```bash
# 1. Open your crontab (opens in nano)
crontab -e

# 2. Go to the bottom, paste this line (replace vboxuser with your username):
*/5 * * * * /home/vboxuser/projects/Self-Study-Tech-Projects/Linux-Lab/scripts/backup.sh >> /home/vboxuser/projects/Self-Study-Tech-Projects/Linux-Lab/data/output/cron-backup.log 2>&1

# 3. Save and exit nano: Ctrl+O → Enter → Ctrl+X

# 4. Verify
crontab -l
```

**Line explained:**

| Part       | Meaning                              |
|------------|--------------------------------------|
| `*/5`      | Every 5 minutes                      |
| `* * * *`  | Every hour / day / month / weekday   |
| `>> file`  | Append output to log file            |
| `2>&1`     | Include errors in the same log       |

> Nano tip: paste from terminal with **right-click** or **Shift+Ctrl+V** — `Ctrl+C` does not copy in nano.

**After ~5 minutes, verify it ran:**

```bash
ls data/output/
cat data/output/cron-backup.log
```

**To stop the cron job:**

```bash
crontab -e   # find the line, delete it (Ctrl+K), save and exit
crontab -l   # verify it's gone
```

- Removing the line stops future runs — cron will not execute it again.
- To stop a currently running instance: `pgrep -a backup.sh` then `kill <PID>`.
- To remove **all** cron jobs at once: `crontab -r` (destructive — use carefully).

The reference cron line is also in `cron/backup.cron`.

---

## Git Workflow

```bash
# --- On Windows (PowerShell / Git Bash) ---
cd "...\Linux-Lab"
git add .
git commit -m "your message"
git push origin master

# --- On Ubuntu ---
cd ~/projects/Self-Study-Tech-Projects
git pull origin master
cd Linux-Lab   # all scripts run from here
```

---

## Practice Checklist

- [ ] Run all 10 lab scripts in order
- [ ] Read `Linux Commands.pdf` alongside each script
- [ ] Use `grep`, `find`, and `ps` manually in the terminal
- [ ] Create and extract your own `.tar.gz` archive
- [ ] Install and start the systemd user service; check `journalctl`
- [ ] Add the cron job and verify it creates backups
- [ ] (Optionally) Modify `scripts/hello.sh` and push from Windows; pull on Ubuntu
- [ ] Write a new script in `scripts/` that sources `common.sh`

---

## Reference

- `Linux Commands.pdf` — command handbook
- `notes/commands.md` — quick reference for commands used in this lab
- `data/input/app.log` — sample log file for grep/search practice
