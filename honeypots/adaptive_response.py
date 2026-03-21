# honeypots/adaptive_response.py
"""
Adaptive Response Engine — selects deception strategy
based on attacker profile.

4 strategies:
  deny_fast     → immediate rejection (waste no time)
  slow_response → artificial delays (waste attacker time)
  fake_success  → accept with fake credentials, log commands
  full_fake_env → complete fake shell, maximum intelligence
"""

import time
import random
import threading


# ── Deception strategies ───────────────────────────

class DenyFast:
    """
    For script kiddies and scanners.
    Reject immediately — don't waste server resources.
    """
    NAME = 'deny_fast'

    @staticmethod
    def respond(conn, profile_type: str) -> dict:
        try:
            conn.send(b'SSH-2.0-OpenSSH_8.9p1 Ubuntu-3ubuntu0.6\r\n')
            time.sleep(0.1)
            conn.send(b'Permission denied (publickey,password).\r\n')
        except Exception:
            pass
        return {
            'strategy':       'deny_fast',
            'interaction':    'rejected',
            'intel_collected': False,
            'commands':       [],
        }


class SlowResponse:
    """
    For botnet nodes.
    Artificial delays burn attacker time and CPU.
    Tarpitting — each response takes 3-8 seconds.
    """
    NAME = 'slow_response'

    @staticmethod
    def respond(conn, profile_type: str) -> dict:
        try:
            # Slow banner
            conn.send(b'SSH-2.0-OpenSSH_8.9p1 Ubuntu-3ubuntu0.6\r\n')

            # Multiple slow fake auth attempts
            for i in range(random.randint(3, 6)):
                time.sleep(random.uniform(3.0, 8.0))
                try:
                    data = conn.recv(512)
                    if not data:
                        break
                    conn.send(
                        b'Permission denied, please try again.\r\n'
                    )
                except Exception:
                    break

        except Exception:
            pass

        return {
            'strategy':        'slow_response',
            'interaction':     'tarpitted',
            'intel_collected': False,
            'commands':        [],
            'delay_applied':   True,
        }


class FakeSuccess:
    """
    For credential stuffers and targeted attackers.
    Accept login with fake credentials.
    Collect commands they run — pure intelligence.
    """
    NAME = 'fake_success'

    FAKE_PROMPTS = [
        b'ubuntu@ip-172-31-45-12:~$ ',
        b'root@honeypot-prod-01:~# ',
        b'admin@web-server-02:~$ ',
    ]

    FAKE_RESPONSES = {
        b'whoami':          b'root\r\n',
        b'id':              b'uid=0(root) gid=0(root) groups=0(root)\r\n',
        b'uname -a':        b'Linux ip-172-31-45-12 5.15.0-1031-aws #35-Ubuntu SMP Fri Feb 10 02:07:47 UTC 2023 x86_64 x86_64 x86_64 GNU/Linux\r\n',
        b'pwd':             b'/root\r\n',
        b'ls':              b'backup  credentials.txt  deploy.sh  .ssh\r\n',
        b'cat /etc/passwd': b'root:x:0:0:root:/root:/bin/bash\ndaemon:x:1:1:daemon:/usr/sbin:/usr/sbin/nologin\n',
        b'ifconfig':        b'eth0: flags=4163<UP,BROADCAST,RUNNING,MULTICAST>  mtu 9001\n        inet 172.31.45.12  netmask 255.255.240.0  broadcast 172.31.47.255\n',
        b'ps aux':          b'USER       PID %CPU %MEM    VSZ   RSS TTY      STAT START   TIME COMMAND\nroot         1  0.0  0.1 168140 13172 ?        Ss   09:15   0:01 /sbin/init\n',
        b'history':         b'1  ssh admin@10.0.1.5\n2  cat /etc/shadow\n3  wget http://update-server.internal/deploy.sh\n',
    }

    @classmethod
    def respond(cls, conn, profile_type: str) -> dict:
        commands_collected = []
        prompt = random.choice(cls.FAKE_PROMPTS)

        try:
            conn.send(b'SSH-2.0-OpenSSH_8.9p1 Ubuntu-3ubuntu0.6\r\n')
            time.sleep(0.5)

            # Fake successful login
            conn.send(
                b'Last login: Mon Mar 18 14:23:11 2026 '
                b'from 10.0.0.1\r\n'
            )
            conn.send(
                b'Welcome to Ubuntu 22.04.2 LTS '
                b'(GNU/Linux 5.15.0-1031-aws x86_64)\r\n\r\n'
            )
            conn.send(prompt)

            # Collect commands for up to 2 minutes
            conn.settimeout(120)
            while True:
                try:
                    data = conn.recv(256)
                    if not data:
                        break

                    cmd = data.strip()
                    if cmd:
                        commands_collected.append(
                            cmd.decode('utf-8', errors='replace')
                        )

                    # Send fake response
                    response = cls.FAKE_RESPONSES.get(
                        cmd,
                        b'bash: command not found\r\n'
                    )
                    conn.send(response)
                    conn.send(prompt)

                except Exception:
                    break

        except Exception:
            pass

        return {
            'strategy':        'fake_success',
            'interaction':     'engaged',
            'intel_collected': len(commands_collected) > 0,
            'commands':        commands_collected,
            'fake_prompt':     prompt.decode('utf-8', errors='replace'),
        }


class FullFakeEnv:
    """
    For APT actors.
    Full fake environment — looks like a real compromised server.
    Maximum intelligence collection.
    Plants fake sensitive files as honeytokens.
    """
    NAME = 'full_fake_env'

    HONEYTOKEN_FILES = {
        b'cat credentials.txt':
            b'[AWS]\naws_access_key_id = AKIAIOSFODNN7EXAMPLE\naws_secret_access_key = wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY\nregion = us-east-1\n',
        b'cat .ssh/id_rsa':
            b'-----BEGIN RSA PRIVATE KEY-----\nMIIEowIBAAKCAQEA0Z3VS5JJcds3xHn/ygWep4PAtEsHAAAAAAAAAAAAAAAAAAAAAA\n[HONEYTOKEN - ACCESS LOGGED]\n-----END RSA PRIVATE KEY-----\n',
        b'cat deploy.sh':
            b'#!/bin/bash\n# Internal deployment script\nDB_HOST=db-prod-01.internal\nDB_PASS=Pr0d_S3cr3t_2024!\nssh deploy@10.0.1.5 "cd /app && git pull"\n',
    }

    FAKE_PROMPTS = [
        b'root@prod-web-01:~# ',
        b'root@aws-bastion:~# ',
    ]

    @classmethod
    def respond(cls, conn, profile_type: str) -> dict:
        commands_collected = []
        honeytoken_accessed = []
        prompt = cls.FAKE_PROMPTS[0]

        try:
            conn.send(b'SSH-2.0-OpenSSH_8.9p1 Ubuntu-3ubuntu0.6\r\n')
            time.sleep(1.0)

            conn.send(
                b'\r\n'
                b'  ___  _    _ ___\r\n'
                b' / _ \\| |  | |  _ \\\r\n'
                b'| | | | |  | | |_) |\r\n'
                b'| |_| | |__| |  _ <\r\n'
                b' \\___/ \\____/|_| \\_\\\r\n'
                b'\r\n'
                # b'Ubuntu 22.04.3 LTS — Production Server\r\n'
                b'System information as of Mon Mar 18 2026\r\n\r\n'
                b'  Load average: 0.08, 0.12, 0.09\r\n'
                b'  Processes:    142\r\n'
                b'  Users:        1\r\n\r\n'
            )
            conn.send(prompt)

            # Extended session — 5 minutes for APT
            conn.settimeout(300)

            all_responses = {
                **FakeSuccess.FAKE_RESPONSES,
                **cls.HONEYTOKEN_FILES,
                b'ls -la': (
                    b'total 48\r\n'
                    b'drwx------ 5 root root 4096 Mar 18 09:15 .\r\n'
                    b'drwxr-xr-x 20 root root 4096 Mar 10 08:22 ..\r\n'
                    b'-rw------- 1 root root  892 Mar 18 14:22 .bash_history\r\n'
                    b'-rw-r--r-- 1 root root 3526 Mar 10 08:22 .bashrc\r\n'
                    b'drwx------ 2 root root 4096 Mar 15 11:30 .ssh\r\n'
                    b'-rw-r--r-- 1 root root  156 Mar 16 09:45 credentials.txt\r\n'
                    b'-rwxr-xr-x 1 root root  512 Mar 17 15:20 deploy.sh\r\n'
                    b'drwxr-xr-x 3 root root 4096 Mar 12 10:15 backup\r\n'
                ),
            }

            while True:
                try:
                    data = conn.recv(256)
                    if not data:
                        break

                    cmd = data.strip()
                    if cmd:
                        cmd_str = cmd.decode('utf-8', errors='replace')
                        commands_collected.append(cmd_str)

                        # Check if honeytoken accessed
                        if cmd in cls.HONEYTOKEN_FILES:
                            honeytoken_accessed.append(cmd_str)
                            print(
                                f"[!!!] HONEYTOKEN ACCESSED: "
                                f"{cmd_str}"
                            )

                    response = all_responses.get(
                        cmd,
                        b'bash: command not found\r\n'
                    )
                    conn.send(response)
                    conn.send(prompt)

                except Exception:
                    break

        except Exception:
            pass

        return {
            'strategy':           'full_fake_env',
            'interaction':        'deep_engaged',
            'intel_collected':    len(commands_collected) > 0,
            'commands':           commands_collected,
            'honeytoken_accessed': honeytoken_accessed,
            'apt_confirmed':      len(honeytoken_accessed) > 0,
        }


# ── Strategy selector ──────────────────────────────

STRATEGIES = {
    'deny_fast':    DenyFast,
    'slow_response': SlowResponse,
    'fake_success': FakeSuccess,
    'full_fake_env': FullFakeEnv,
}


def select_and_execute(
    conn,
    deception_strategy: str,
    profile_type:       str,
) -> dict:
    """Select and execute the appropriate deception strategy."""
    strategy_class = STRATEGIES.get(deception_strategy, DenyFast)
    print(
        f"[Adaptive] Strategy: {deception_strategy} "
        f"for {profile_type}"
    )
    return strategy_class.respond(conn, profile_type)