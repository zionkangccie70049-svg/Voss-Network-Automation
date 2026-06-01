import os
import sys
from netmiko import ConnectHandler, NetmikoTimeoutException, NetmikoAuthenticationException
from datetime import datetime

# inventory.py is gitignored — copy inventory.example.py → inventory.py and fill in your devices
from inventory import SWITCHES

# ─────────────────────────────────────────────
#  Config  (credentials via environment variables)
# ─────────────────────────────────────────────
USERNAME    = os.environ.get("NETWORK_USERNAME")
PASSWORD    = os.environ.get("NETWORK_PASSWORD")
DEVICE_TYPE = "extreme_vsp"
BACKUP_DIR  = os.environ.get("BACKUP_DIR", "/opt/network-backups")

# ─────────────────────────────────────────────
#  Main
# ─────────────────────────────────────────────
def backup_switch(device_info: dict, timestamp: str) -> bool:
    hostname = device_info["host"]
    ip       = device_info["ip"]

    conn_params = {
        "device_type": DEVICE_TYPE,
        "host":        ip,
        "username":    USERNAME,
        "password":    PASSWORD,
    }

    try:
        net_connect = ConnectHandler(**conn_params)
        net_connect.enable()
        config = net_connect.send_command("show running")
        net_connect.disconnect()

        # 날짜별 서브폴더: /opt/network-backups/MMDDYYYY/
        date_dir = os.path.join(BACKUP_DIR, timestamp[:8])
        os.makedirs(date_dir, exist_ok=True)

        filename = os.path.join(date_dir, f"{ip}_{hostname}_{timestamp}.txt")
        with open(filename, "w") as f:
            f.write(config)

        print(f"  [OK]   {hostname} ({ip})  →  {filename}")
        return True

    except NetmikoAuthenticationException:
        print(f"  [FAIL] {hostname} ({ip})  —  authentication error")
    except NetmikoTimeoutException:
        print(f"  [FAIL] {hostname} ({ip})  —  connection timeout")
    except Exception as e:
        print(f"  [FAIL] {hostname} ({ip})  —  {e}")

    return False


def main():
    if not USERNAME or not PASSWORD:
        raise SystemExit("ERROR: NETWORK_USERNAME / NETWORK_PASSWORD env vars not set")

    timestamp = datetime.now().strftime("%m%d%Y_%H-%M-%S")

    print(f"\nBackup directory : {BACKUP_DIR}")
    print(f"Starting backup  — {len(SWITCHES)} devices\n")

    results = [backup_switch(sw, timestamp) for sw in SWITCHES]

    ok   = results.count(True)
    fail = results.count(False)
    print(f"\nDone  ✓ {ok} succeeded   ✗ {fail} failed   ({len(SWITCHES)} total)")

    if fail > 0:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
