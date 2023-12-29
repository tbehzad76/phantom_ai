
# Phantom ai

A trading cryptocurrency bot for bingx

## Installation

Install phantom ai

1-clone project to root of your server

2-Create a Service File in the folder /lib/systemd/system/ as phantom_ai.service and save it 
With Below contents in this file

```
[Unit]
Description=phantom ai service
After=multi-user.target
[Service]
User=root
Type=simple
Environment=PYTHONUNBUFFERED=1
WorkingDirectory=/root/tradingBot
ExecStart=/usr/bin/python3 /root/tradingBot/Phantom_AI.py
ExecReload=/bin/kill -HUP $MAINPID
KillMode=process
Restart=on-failure
RestartSec=42s
[Install]
WantedBy=multi-user.target
```

3-Reload the service files to include the new service.
```
sudo systemctl daemon-reload
```
4-Start Phantom AI service
```
sudo systemctl start phantom_ai.service
```

5-Check the status of Phantom AI
```
sudo systemctl status phantom_ai.service
```
6-Enable Phantom AI on every reboot
```
sudo systemctl enable phantom_ai.service
```
7-Disable Phantom AI on every reboot
```
sudo systemctl disable phantom_ai.service
```



    