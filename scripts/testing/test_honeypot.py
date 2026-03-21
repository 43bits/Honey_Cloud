# scripts/test_honeypot.py
"""
Simulates different attacker profiles against the honeypot.
"""
import socket
import time
import threading

def simulate_script_kiddie():
    """Single quick connection — should trigger deny_fast."""
    s = socket.socket()
    s.connect(('127.0.0.1', 2222))
    s.recv(256)
    s.send(b'admin:admin\n')
    s.recv(256)
    s.close()
    print('[Test] Script kiddie sent')

def simulate_botnet(count=10):
    """Rapid multiple connections — should trigger slow_response."""
    for i in range(count):
        try:
            s = socket.socket()
            s.settimeout(2)
            s.connect(('127.0.0.1', 2222))
            s.recv(256)
            s.send(f'user{i}:pass{i}\n'.encode())
            time.sleep(0.1)
            s.close()
        except Exception:
            pass
    print('[Test] Botnet simulation sent')

def simulate_credential_stuffer():
    """Many unique username/password combos — fake_success."""
    s = socket.socket()
    s.settimeout(30)
    s.connect(('127.0.0.1', 2222))
    s.recv(256)

    users = ['admin','root','user','test','deploy',
             'backup','postgres','mysql','redis','ubuntu',
             'pi','ansible','oracle','hadoop','elastic']
    passes = ['password','123456','admin','letmein',
              'welcome','monkey','dragon','master',
              'pass','qwerty','login','abc123']

    for u in users:
        for p in passes[:3]:
            try:
                s.send(f'{u}:{p}\n'.encode())
                time.sleep(0.3)
                s.recv(256)
            except Exception:
                break
    s.close()
    print('[Test] Credential stuffer sent')

def simulate_apt():
    """Slow targeted attack — full_fake_env."""
    s = socket.socket()
    s.settimeout(60)
    s.connect(('127.0.0.1', 2222))
    s.recv(256)

    # APT usernames — specific high-value targets
    apt_users = ['administrator', 'sysadmin', 'jenkins', 'gitlab']
    for u in apt_users:
        try:
            s.send(f'{u}:C0mpl3x_P@ss!\n'.encode())
            time.sleep(3.0)   # slow deliberate timing
            s.recv(256)
        except Exception:
            break
    s.close()
    print('[Test] APT simulation sent')

if __name__ == '__main__':
    print('Testing all 4 attacker profiles...\n')

    print('1. Script kiddie...')
    simulate_script_kiddie()
    time.sleep(2)

    print('2. Botnet node...')
    simulate_botnet(12)
    time.sleep(3)

    print('3. Credential stuffer...')
    simulate_credential_stuffer()
    time.sleep(3)

    print('4. APT actor...')
    simulate_apt()
    time.sleep(5)

    print('\nDone. Check honeypot terminal for profile detections.')
    print('Check logs/ssh_adaptive.json for full telemetry.')