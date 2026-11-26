"""Tabela de pontuação persistente em JSON."""
import json
import os
from datetime import datetime

LEADERBOARD_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "leaderboard.json")

def _int(value):
    try:
        return int(value)
    except (TypeError, ValueError):
        return 0


def _same_session(prev, cur, max_gap_hours=3):
    """Registro antigo (sem "sessao") continua a partida anterior do mesmo
    participante quando os contadores só cresceram e passou pouco tempo."""
    if cur.get('modo') == 'competicao' or prev.get('modo') == 'competicao':
        return False
    for k in ('pontuacao', 'acertos', 'erros'):
        if _int(cur.get(k)) < _int(prev.get(k)):
            return False
    try:
        gap = datetime.fromisoformat(cur['data']) - datetime.fromisoformat(prev['data'])
    except (KeyError, TypeError, ValueError):
        return False
    return gap.total_seconds() <= max_gap_hours * 3600


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
        # ranking de sessões do modo clássico (ordenado por nota); as rodadas
        # da competição não têm nota e entram só no ranking geral (totals)
        entries = [e for e in self.load() if e.get('modo') != 'competicao']
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

    def totals(self):
        """Ranking geral: pontuação total de cada participante somando todas
        as partidas que jogou (modo clássico e rodadas da competição).

        Os registros de uma mesma partida são acumulados (ex.: salvo na vitória
        de Matemática e de novo ao perder os corações), então cada partida
        conta só pelo seu último registro. O participante é identificado pelo
        nome, sem diferenciar maiúsculas/minúsculas.
        """
        entries = sorted(self.load(), key=lambda e: str(e.get('data', '')))
        sessions = {}       # (participante, sessão) -> último registro
        legacy_last = {}    # participante -> (sessão, registro) sem campo "sessao"
        for i, e in enumerate(entries):
            nome = str(e.get('nome_jogador') or '').strip()
            if not nome:
                continue
            pid = nome.casefold()
            sid = e.get('sessao')
            if not sid:
                # registros antigos, anteriores ao campo "sessao"
                prev = legacy_last.get(pid)
                sid = prev[0] if prev and _same_session(prev[1], e) else f"legado-{i}"
                legacy_last[pid] = (sid, e)
            sessions[(pid, sid)] = e

        players = {}
        for (pid, _), e in sessions.items():
            p = players.setdefault(pid, {
                'nome': '', 'pontuacao': 0, 'partidas': 0, 'acertos': 0,
                'erros': 0, 'modos': set(), 'data': '',
            })
            p['pontuacao'] += _int(e.get('pontuacao'))
            p['acertos'] += _int(e.get('acertos'))
            p['erros'] += _int(e.get('erros'))
            p['partidas'] += 1
            p['modos'].add('Competição' if e.get('modo') == 'competicao' else 'Clássico')
            data = str(e.get('data', ''))
            if data >= p['data']:          # mostra o nome como foi digitado por último
                p['data'] = data
                p['nome'] = str(e.get('nome_jogador')).strip()

        result = []
        for p in players.values():
            p['modos'] = ' e '.join(sorted(p['modos']))
            result.append(p)
        result.sort(key=lambda p: (-p['pontuacao'], -p['acertos'], p['erros'], p['nome'].casefold()))
        return result

    def clear(self):
        try:
            if os.path.exists(self.path):
                os.remove(self.path)
            return True
        except Exception:
            return False
