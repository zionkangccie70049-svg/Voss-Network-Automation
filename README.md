# Extreme VSP / 5520 Config Backup Automation

Automated configuration backup for Extreme Networks VSP and ERS 5520 switches using Python + Netmiko, integrated with a GitLab CI/CD pipeline.

## Overview

- Connects to each switch via SSH using Netmiko
- Runs `show running` and saves output to a timestamped file
- Organizes backups into daily subdirectories (`/opt/network-backups/MMDDYYYY/`)
- Runs on a self-hosted GitLab Runner (shell executor) — backups persist on the runner server
- Pipeline is triggered manually via GitLab UI

## Stack

| Tool | Purpose |
|---|---|
| Python 3 | Core scripting |
| Netmiko | SSH to network devices |
| GitLab CI/CD | Pipeline automation |
| GitLab Runner (shell) | Self-hosted execution + local file storage |

## Project Structure

```
.
├── vspbackup.py            # Main backup script
├── inventory.example.py    # Device list template (copy → inventory.py)
├── .gitlab-ci.yml          # CI/CD pipeline definition
├── .gitignore
└── README.md
```

## Setup

### 1. Device Inventory

```bash
cp inventory.example.py inventory.py
# Edit inventory.py with your actual hostnames and IPs
```

`inventory.py` is gitignored and will never be committed.

### 2. Runner Server (one-time)

```bash
sudo mkdir -p /opt/network-backups
sudo chown gitlab-runner:gitlab-runner /opt/network-backups
pip3 install netmiko paramiko --break-system-packages
```

### 3. GitLab CI/CD Variables

In GitLab → **Settings → CI/CD → Variables**, add:

| Variable | Description |
|---|---|
| `NETWORK_USERNAME` | Switch SSH username (masked) |
| `NETWORK_PASSWORD` | Switch SSH password (masked) |

### 4. Run

Go to **GitLab → CI/CD → Pipelines → Run pipeline** (manual trigger).

## Backup Storage

Backups are saved directly on the runner server:

```
/opt/network-backups/
└── 06012026/
    ├── 10.31.1.1_Core-Switch_06012026_18-30-00.txt
    ├── 10.31.1.3_Distribution-SW_06012026_18-30-05.txt
    └── ...
```

## Error Handling

- Auth failures and timeouts are caught per-device and logged — one failed device does not stop the rest
- If any device fails, the pipeline exits with code 1 (marked as Failed in GitLab)

## Supported Platforms

Tested on Extreme Networks VSP 7400 and ERS 5520 series.
