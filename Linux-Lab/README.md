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
systemctl --user daemon-reload
systemctl --user start linux-lab
systemctl --user status linux-lab
systemctl --user stop linux-lab
systemctl --user restart linux-lab

# 3. Follow logs
journalctl --user -u linux-lab -f
```

---

## Cron Job

Runs `backup.sh` every 5 minutes.

```bash
# 1. Open your crontab
crontab -e

# 2. Paste this line (replace <username> with your actual username):
*/5 * * * * /home/<username>/projects/Linux-Lab/scripts/backup.sh >> /home/<username>/projects/Linux-Lab/data/output/cron-backup.log 2>&1

# 3. Verify
crontab -l
```

The reference cron line is also in `cron/backup.cron`.

---

## Git Workflow

```bash
# --- On Windows (PowerShell / Git Bash) ---
cd "E:\Software\GitHub Self-Study\Linux-Lab"
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
- [ ] Modify `scripts/hello.sh` and push from Windows; pull on Ubuntu
- [ ] Write a new script in `scripts/` that sources `common.sh`

---

## Reference

- `Linux Commands.pdf` — command handbook (do not modify)
- `notes/commands.md` — quick reference for commands used in this lab
- `data/input/app.log` — sample log file for grep/search practice
