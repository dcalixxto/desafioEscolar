"""Tabela de pontuação persistente em JSON."""
import json
import os
from datetime import datetime

LEADERBOARD_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "leaderboard.json")

class Leaderboard:
    def __init__(self, path=None):
        self.path = path or LEADERBOARD_PATH
        os.makedirs(os.path.dirname(self.path), exist_ok=True)

    def load(self):
        if not os.path.exists(self.path):
            return []
        try:
            with open(self.path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            if isinstance(data, list):
                return data
        except Exception:
            pass
        return []

    def save_all(self, entries):
        try:
            with open(self.path, 'w', encoding='utf-8') as f:
                json.dump(entries, f, ensure_ascii=False, indent=2)
            return True
        except Exception:
            return False

    def add_entry(self, entry):
        entries = self.load()
        entries.append(entry)
        # ordenar: nota desc, pontuacao desc, erros asc, data desc
        def key(e):
            try:
                nota = float(e.get('nota_final', 0))
            except Exception:
                nota = 0.0
            try:
                pts = int(e.get('pontuacao', 0))
            except Exception:
                pts = 0
            try:
                errs = int(e.get('erros', 0))
            except Exception:
                errs = 9999
            data = e.get('data', '')
            return (-nota, -pts, errs, data)
        entries.sort(key=key)
        self.save_all(entries)
        return entries

    def top(self, n=10):
        entries = self.load()
        def key(e):
            try:
                nota = float(e.get('nota_final', 0))
            except Exception:
                nota = 0.0
            try:
                pts = int(e.get('pontuacao', 0))
            except Exception:
                pts = 0
            try:
                errs = int(e.get('erros', 0))
            except Exception:
                errs = 9999
            data = e.get('data', '')
            return (-nota, -pts, errs, data)
        entries.sort(key=key)
        return entries[:n]

    def clear(self):
        try:
            if os.path.exists(self.path):
                os.remove(self.path)
            return True
        except Exception:
            return False
