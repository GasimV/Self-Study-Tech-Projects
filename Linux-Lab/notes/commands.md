# Commands Used in This Lab

## Files & Directories
```
mkdir -p dir/subdir          # create nested dirs
cp src dest                  # copy file
mv src dest                  # move / rename
ls -lh dir                   # list with sizes
find dir -name "file.txt"    # locate file
rm file                      # delete file
```

## Permissions
```
chmod +x script.sh           # make executable
chmod 755 file               # rwxr-xr-x
chmod 600 file               # rw-------
ls -l                        # show permissions
```

## Search
```
grep "pattern" file          # search in file
grep -i "pattern" file       # case-insensitive
grep -c "pattern" file       # count matches
grep -r "pattern" dir        # recursive
```

## Processes
```
ps aux                       # all processes
ps aux | grep '[b]ash'       # find bash procs
pgrep -a python              # python by name
kill PID                     # terminate process
echo $$                      # current PID
```

## Network
```
ip a                         # show IP addresses
ping -c 2 8.8.8.8            # ping 2 times
curl -I https://example.com  # HTTP headers only
```

## Archives
```
tar -czf archive.tar.gz dir  # create compressed archive
tar -tzf archive.tar.gz      # list contents
tar -xzf archive.tar.gz      # extract
```

## Logs
```
head -5 file                 # first 5 lines
tail -5 file                 # last 5 lines
tail -f file                 # follow live
wc -l file                   # line count
```

## Environment
```
export VAR=value             # set variable
echo $VAR                    # print variable
env | sort                   # list all env vars
```

## systemd (user)
```
systemctl --user daemon-reload
systemctl --user start linux-lab
systemctl --user status linux-lab
systemctl --user stop linux-lab
journalctl --user -u linux-lab -f
```

## cron
```
crontab -e                   # edit cron jobs
crontab -l                   # list cron jobs
# */5 * * * * /path/script   # every 5 minutes
```
