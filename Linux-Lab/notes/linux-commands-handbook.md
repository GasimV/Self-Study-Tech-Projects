# Linux Commands Handbook

> Format: Command → what it does

---

## Table of Contents

- [1. Linux Command Handbook (Beginner Core)](#1-linux-command-handbook-beginner-core)
  - [systemd & Services](#systemd--services)
    - [systemctl](#systemctl)
    - [journalctl](#journalctl)
    - [systemd Concept](#systemd-concept)
  - [File & Directory Management](#file--directory-management)
  - [File Viewing & Editing](#file-viewing--editing)
  - [Search & Discovery](#search--discovery)
  - [Processes & System Monitoring](#processes--system-monitoring)
  - [Package Management](#package-management)
  - [Permissions & Ownership](#permissions--ownership)
  - [Networking](#networking)
  - [Terminal Productivity](#terminal-productivity)
  - [Service Example (nginx)](#service-example-nginx)
  - [Core Set — Must Memorize First](#core-set--must-memorize-first)
  - [Final Mental Model](#final-mental-model)
- [2. Finding Python Processes](#2-finding-python-processes)
  - [Basic Command](#basic-command)
  - [Better Version (no self-match)](#better-version-no-self-match)
  - [Best Version (pgrep)](#best-version-pgrep)
  - [Summary](#summary)
- [3. Monitor Python Process in Real Time](#3-monitor-python-process-in-real-time)
  - [top (built-in)](#top-built-in)
  - [htop (interactive)](#htop-interactive)
  - [watch + ps (live refresh)](#watch--ps-live-refresh)
  - [Monitor by PID](#monitor-by-pid)
  - [Logs via journalctl](#logs-via-journalctl)
  - [When to Use What](#when-to-use-what)
  - [Pro Tip — Sort in top](#pro-tip--sort-in-top)
- [4. SSH — Remote Access](#4-ssh--remote-access)
  - [Connect](#connect)
  - [Custom Port](#custom-port)
  - [Copy Files (scp)](#copy-files-scp)
  - [Sync (rsync over SSH)](#sync-rsync-over-ssh)
  - [SSH Keys (no password)](#ssh-keys-no-password)
  - [Run Remote Command](#run-remote-command)
  - [Mount Remote Folder (sshfs)](#mount-remote-folder-sshfs)
  - [Check SSH Service](#check-ssh-service)
  - [Minimal Memory Set](#minimal-memory-set)
  - [Lab Setup](#lab-setup)
  - [Practice Routine](#practice-routine)
- [5. Linux Networking — Copy / Move Between Systems](#5-linux-networking--copy--move-between-systems)
  - [scp — Secure Copy](#scp--secure-copy)
  - [rsync — Efficient Sync](#rsync--efficient-sync)
  - [sftp — Interactive Transfer](#sftp--interactive-transfer)
  - [ssh + tar — Bulk Transfer](#ssh--tar--bulk-transfer)
  - [wget — Download from URL](#wget--download-from-url)
  - [curl — Flexible Transfer](#curl--flexible-transfer)
  - [sshfs — Mount Remote Directory](#sshfs--mount-remote-directory)
  - [netcat (nc) — Raw Transfer](#netcat-nc--raw-transfer)
  - [Decision Table](#decision-table)
  - [Real-World Scenarios](#real-world-scenarios)

---

## 1. Linux Command Handbook (Beginner Core)

---

### systemd & Services

#### systemctl

```bash
systemctl start <service>            # start a service
systemctl stop <service>             # stop a service
systemctl restart <service>          # restart a service
systemctl reload <service>           # reload config without stopping
systemctl status <service>           # show service status
systemctl enable <service>           # start service at boot
systemctl disable <service>          # prevent start at boot
systemctl list-units --type=service  # list running services
systemctl --failed                   # show failed services
(sudo) systemctl reboot              # reboot system
(sudo) systemctl poweroff            # shut down system
```

---

#### journalctl

```bash
journalctl                      # show all logs
journalctl -u <service>         # logs for specific service
journalctl -f                   # follow logs live
journalctl -u <service> -f      # follow logs of a service
journalctl -xe                  # latest logs + explanations
journalctl -u <service> -xe     # detailed logs for a service
journalctl -p err -b            # show errors from current boot
```

---

#### systemd Concept

- `.service` file → defines how a service runs
- Located in `/etc/systemd/system/` or `/lib/systemd/system/`

---

### File & Directory Management

```bash
ls                  # list files
ls -la              # list all files (including hidden) with details
cd <dir>            # change directory
pwd                 # show current directory (Print Working Directory)
mkdir <name>        # create directory
rm <file>           # delete file
rm -r <dir>         # delete directory recursively
cp <src> <dest>     # copy file
mv <src> <dest>     # move or rename file
```

---

### File Viewing & Editing

```bash
cat <file>                       # print file contents
less <file>                      # view file with scrolling (q to exit)
head <file>                      # show first lines
tail <file>                      # show last lines
tail -f <file>                   # follow file updates live
nano <file>                      # open simple text editor
echo "text" > file               # write text to file (overwrites)
echo "text" >> file.txt          # append text to existing file
touch filename.txt               # create an empty file
touch file1.txt file2.txt        # create multiple empty files
cat > filename.txt               # create file and type content interactively
                                 # (Ctrl+D to save, Ctrl+C to cancel)
```

---

### Search & Discovery

```bash
grep "text" <file>      # search text in file
grep -r "text" .        # search recursively in current directory
find . -name <file>     # find file by name (run from parent directory)
which <command>         # show path of a command
```

---

### Processes & System Monitoring

```bash
ps aux    # list all processes
          # ps = process status; a = all users; u = user format; x = no terminal
top       # real-time system usage
htop      # improved process viewer (if installed)
kill <pid>  # stop process by ID
```

---

### Package Management

**Debian / Ubuntu:**

```bash
sudo apt update          # update package list
sudo apt install <pkg>   # install package
sudo apt remove <pkg>    # remove package
```

**Fedora:**

```bash
sudo dnf install <pkg>   # install package
```

---

### Permissions & Ownership

```bash
chmod +x <file>        # make file executable
chmod 755 <file>       # set permissions (rwxr-xr-x)
chown user: <file>     # change file owner
```

---

### Networking

```bash
ping <host>    # test connectivity (use domain name or IP, not full https:// URL)
curl '<url>'   # fetch data from URL (wrap URL in quotes if it contains special chars)
wget <url>     # download file
ip a           # show IP addresses
```

---

### Terminal Productivity

```bash
history   # show command history
clear     # clear terminal screen
sudo !!   # rerun last command with sudo
```

---

### Service Example (nginx)

```bash
systemctl start nginx      # start nginx
systemctl status nginx     # check nginx status
journalctl -u nginx        # view nginx logs
```

---

### Core Set — Must Memorize First

```bash
ls                  # list files
cd                  # navigate
pwd                 # current location
cp / mv / rm        # manage files
cat / less          # read files
grep                # search
systemctl           # manage services
journalctl          # view logs
```

---

### Final Mental Model

| Category               | What it is                        |
|------------------------|-----------------------------------|
| Files                  | Everything stored                 |
| Processes              | Everything running                |
| Services (`.service`)  | Managed background apps           |
| Logs (`journalctl`)    | What happened                     |

---

## 2. Finding Python Processes

#### Basic Command

```bash
ps aux | grep python
```

- `ps aux` → list all running processes
- `|` → pipe output to next command
- `grep python` → filter lines containing "python"

> **Issue:** also shows the `grep` process itself in results.

---

#### Better Version (no self-match)

```bash
ps aux | grep '[p]ython'
```

- `[p]ython` matches "python" but does **not** match the grep command itself.

---

#### Best Version (pgrep)

```bash
pgrep -af python
```

- Shows only Python processes, clean and fast.

---

#### Summary

| Command                        | Notes                        |
|-------------------------------|------------------------------|
| `ps aux \| grep python`        | Basic, shows grep itself     |
| `ps aux \| grep '[p]ython'`    | Avoids self-match            |
| `pgrep -a python`              | Best — clean output          |

---

## 3. Monitor Python Process in Real Time

#### top (built-in)

```bash
top
# Then: Shift+L → type "python" → Enter
```

Shows: live CPU, memory usage, PIDs.

---

#### htop (interactive)

```bash
htop
# Then: F3 → type "python"
```

Easier to read, colorful UI, can scroll/filter/kill.

---

#### watch + ps (live refresh)

```bash
watch -n 1 "ps aux | grep '[p]ython'"
```

Updates every 1 second, shows only Python processes.

---

#### Monitor by PID

```bash
pgrep -af python   # get PID
top -p <PID>       # monitor that process
```

---

#### Logs via journalctl

```bash
journalctl -u <service> -f   # real-time log output (if running as a service)
```

---

#### When to Use What

| Goal                   | Tool                    |
|------------------------|-------------------------|
| Quick check            | `ps aux \| grep`        |
| Live system view       | `top`                   |
| Best experience        | `htop`                  |
| Script-friendly        | `watch`                 |
| Logs / debugging       | `journalctl -f`         |

---

#### Pro Tip — Sort in top

While inside `top`:

```
Shift+P  → sort by CPU usage
Shift+M  → sort by memory (%MEM)
Shift+T  → sort by running time (TIME+)
Shift+N  → sort by process ID (PID)
```

---

## 4. SSH — Remote Access

> **SSH (Secure Shell)** — cryptographic protocol for remote login and command execution over an unsecured network. Replaces insecure protocols like Telnet.

---

#### Connect

```bash
ssh user@host
ssh vboxuser@192.168.56.102   # example: connect to VM
```

---

#### Custom Port

```bash
ssh -p <port> user@host   # default port is 22
```

---

#### Copy Files (scp)

```bash
scp file user@host:/path                          # send file to remote
scp user@host:/path/file .                        # receive file from remote
scp test.txt vboxuser@192.168.56.102:/home/vboxuser/   # example
```

---

#### Sync (rsync over SSH)

```bash
rsync -avz dir user@host:/path   # sync directory (only changed files transfer)
```

---

#### SSH Keys (no password)

```bash
ssh-keygen -t ed25519   # generate key pair
ssh-copy-id user@host   # copy public key to server
ssh user@host           # connect without password
```

---

#### Run Remote Command

```bash
ssh user@host "command"
ssh vboxuser@192.168.56.102 "ls -la"   # example
```

---

#### Mount Remote Folder (sshfs)

```bash
sshfs user@host:/remote/path /local/mount   # mount
fusermount -u /local/mount                  # unmount
```

---

#### Check SSH Service

```bash
systemctl status ssh   # ensure SSH server is running
```

---

#### Minimal Memory Set

```bash
ssh user@host       # connect
scp file host:path  # copy file
rsync -avz          # sync directory
ssh-keygen          # create key pair
ssh-copy-id         # enable key-based login
```

---

#### Lab Setup

```bash
# Connect from Windows host to Ubuntu VM via host-only network (enp0s8):
ssh vboxuser@192.168.56.102
```

---

#### Practice Routine

```bash
# 1. Start SSH server on VM:
sudo systemctl start ssh

# 2. Connect from host:
ssh vboxuser@192.168.56.102

# 3. Copy a file:
scp test.txt vboxuser@192.168.56.102:/home/vboxuser/

# 4. Run a remote command:
ssh vboxuser@192.168.56.102 "pwd"
```

> **Mental model:** SSH = remote terminal | SCP = copy files | RSYNC = smart copy

---

## 5. Linux Networking — Copy / Move Between Systems

---

#### scp — Secure Copy

```bash
scp app.py user@192.168.1.10:/home/user/         # send file to server
scp user@192.168.1.10:/var/log/app.log .          # download file from server
```

Use case: quick one-time file transfer.

---

#### rsync — Efficient Sync

```bash
rsync -avz project/ user@192.168.1.10:/home/user/project/       # sync directory
rsync -av --delete backup/ user@server:/data/backup/             # mirror (delete extras)
```

Use case: backups, deployments — only changed files transfer.

---

#### sftp — Interactive Transfer

```bash
sftp user@192.168.1.10   # connect interactively
put app.py               # upload file (inside session)
```

Use case: manually browse and upload/download remote files.

---

#### ssh + tar — Bulk Transfer

```bash
tar czf - project/ | ssh user@192.168.1.10 "tar xzf -"        # send directory
ssh user@server "tar czf - /var/www" | tar xzf -               # receive directory
```

Use case: transfer thousands of small files quickly.

---

#### wget — Download from URL

```bash
wget https://example.com/file.zip            # download file
wget -c https://example.com/large.iso        # resume interrupted download
```

Use case: download packages, datasets, installers.

---

#### curl — Flexible Transfer

```bash
curl -O https://example.com/data.json        # download file
curl -o output.json https://api.site/data    # download with custom filename
curl -I https://example.com                  # show HTTP headers only
```

Use case: fetch API data, test endpoints, scripts.

---

#### sshfs — Mount Remote Directory

```bash
sshfs user@192.168.1.10:/home/user /mnt/remote   # mount remote dir
fusermount -u /mnt/remote                         # unmount
```

Use case: edit remote files as if they are local.

---

#### netcat (nc) — Raw Transfer

```bash
nc -l -p 1234 > backup.tar     # receiver: listen on port 1234
nc 192.168.1.10 1234 < backup.tar   # sender: send file
```

Use case: fast transfer in trusted local networks (no SSH needed).

---

#### Decision Table

| Tool          | Best for                                    |
|---------------|---------------------------------------------|
| `scp`         | Quick one-time copy                         |
| `rsync`       | Backups, deployments, syncing               |
| `sftp`        | Manual file browsing on remote              |
| `tar + ssh`   | Large directory transfers (many files)      |
| `wget/curl`   | Internet downloads / API calls              |
| `sshfs`       | Remote editing (mount as local)             |
| `netcat`      | Fast local transfers (advanced, no SSH)     |

---

#### Real-World Scenarios

```bash
rsync project/ server:/app/           # deploy app
scp server:/var/log/app.log .         # grab logs
rsync --delete backup/ server:/bkp/  # backup server (mirror)
sshfs user@host:/etc /mnt/remote      # edit remote config
wget https://example.com/dataset.zip  # download dataset
curl https://api.site/data            # API automation
```
