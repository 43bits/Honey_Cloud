# api/attack_store.py
from collections import deque
from datetime import datetime
import threading

# Thread-safe storage for last 200 attacks
class AttackStore:
    def __init__(self, maxsize=200):
        self._attacks = deque(maxlen=maxsize)
        self._lock = threading.Lock()
        self._stats = {
            'total': 0,
            'by_type': {},
            'by_risk': {'LOW': 0, 'MEDIUM': 0, 'HIGH': 0, 'CRITICAL': 0},
            'by_port': {},
            'by_country': {}
        }

    def add(self, attack: dict):
        with self._lock:
            # Add arrival index
            attack['id'] = self._stats['total']
            self._stats['total'] += 1
            self._attacks.appendleft(attack)  # newest first

            # Update stats

            atype = attack.get('attack_type', 'Unknown')
            self._stats['by_type'][atype] = self._stats['by_type'].get(atype, 0) + 1

            risk = attack.get('risk_level', 'LOW')
            self._stats['by_risk'][risk] = self._stats['by_risk'].get(risk, 0) + 1

            # port = str(attack.get('port', 'unknown'))
            port = str(attack.get('port_targeted', attack.get('port', 'unknown')))
            self._stats['by_port'][port] = self._stats['by_port'].get(port, 0) + 1

            country = attack.get('country', 'Unknown')
            self._stats['by_country'][country] = self._stats['by_country'].get(country, 0) + 1

    def get_recent(self, limit=50):
        with self._lock:
            return list(self._attacks)[:limit]

    def get_stats(self):
        with self._lock:
            # Top 5 attack types
            top_types = sorted(
                self._stats['by_type'].items(),
                key=lambda x: x[1], reverse=True
            )[:5]

            # Top 5 targeted ports
            top_ports = sorted(
                self._stats['by_port'].items(),
                key=lambda x: x[1], reverse=True
            )[:5]

            # Top 5 source countries
            top_countries = sorted(
                self._stats['by_country'].items(),
                key=lambda x: x[1], reverse=True
            )[:5]

            return {
                'total_attacks': self._stats['total'],
                'by_risk': self._stats['by_risk'],
                'top_attack_types': [{'type': k, 'count': v} for k, v in top_types],
                'top_ports': [{'port': k, 'count': v} for k, v in top_ports],
                'top_countries': [{'country': k, 'count': v} for k, v in top_countries]
            }

    def clear(self):
        with self._lock:
            self._attacks.clear()
            self._stats = {
                'total': 0,
                'by_type': {},
                'by_risk': {'LOW': 0, 'MEDIUM': 0, 'HIGH': 0, 'CRITICAL': 0},
                'by_port': {},
                'by_country': {}
            }


# Global singleton — import this everywhere
store = AttackStore()