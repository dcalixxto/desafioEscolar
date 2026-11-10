"""
Módulo de Efeitos Sonoros Sintetizados Proceduralmente.
Gera efeitos sonoros retrô 8-bit/16-bit diretamente via PyGame Mixer sem depender de arquivos externos.
"""

import math
import struct
import pygame

class SoundManager:
    def __init__(self):
        self.enabled = False
        self.music_channel = None
        self.current_music = None
        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init(frequency=22050, size=-16, channels=1, buffer=512)
            self.sample_rate = 22050
            self.enabled = True
            self.sounds = {
                "blip": self._gen_blip(),
                "step": self._gen_step(),
                "dialog": self._gen_dialog(),
                "door": self._gen_door(),
                "correct": self._gen_chord([523.25, 659.25, 783.99], 0.4),
                "wrong": self._gen_wrong(),
                "fanfare": self._gen_fanfare(),
                "select": self._gen_select(),
                "levelup": self._gen_levelup(),
                "ending_music": self._gen_ending_music(),
            }
        except Exception as e:
            print(f"[SoundManager] Aviso: Áudio desativado ({e})")
            self.enabled = False

    def _create_sound_from_samples(self, samples):
        """Empacota lista de inteiros 16-bit com sinal em pygame.mixer.Sound."""
        raw_data = bytearray()
        for s in samples:
            val = max(-32767, min(32767, int(s)))
            raw_data.extend(struct.pack('<h', val))
        return pygame.mixer.Sound(buffer=bytes(raw_data))

    def _gen_blip(self):
        samples = []
        duration = 0.08
        total_samples = int(self.sample_rate * duration)
        for i in range(total_samples):
            t = i / self.sample_rate
            freq = 600 + (t / duration) * 400
            env = 1.0 - (i / total_samples)
            val = math.sin(2 * math.pi * freq * t) * env * 12000
            samples.append(val)
        return self._create_sound_from_samples(samples)

    def _gen_step(self):
        samples = []
        duration = 0.045
        total_samples = int(self.sample_rate * duration)
        for i in range(total_samples):
            t = i / self.sample_rate
            env = (1.0 - (i / total_samples)) ** 2
            val = (math.sin(2 * math.pi * 140 * t) + 0.35 * math.sin(2 * math.pi * 80 * t)) * env * 3200
            samples.append(val)
        return self._create_sound_from_samples(samples)

    def _gen_dialog(self):
        samples = []
        duration = 0.06
        total_samples = int(self.sample_rate * duration)
        for i in range(total_samples):
            t = i / self.sample_rate
            freq = 520
            env = math.sin(math.pi * (i / total_samples))
            val = math.sin(2 * math.pi * freq * t) * env * 7000
            samples.append(val)
        return self._create_sound_from_samples(samples)

    def _gen_door(self):
        samples = []
        duration = 0.28
        total_samples = int(self.sample_rate * duration)
        for i in range(total_samples):
            t = i / self.sample_rate
            env = 1.0 - (i / total_samples)
            freq1 = 240 - 40 * t
            freq2 = 360 - 30 * t
            val = (math.sin(2 * math.pi * freq1 * t) + math.sin(2 * math.pi * freq2 * t)) * 0.5 * env * 13000
            samples.append(val)
        return self._create_sound_from_samples(samples)

    def _gen_chord(self, freqs, duration):
        samples = []
        total_samples = int(self.sample_rate * duration)
        for i in range(total_samples):
            t = i / self.sample_rate
            env = (1.0 - (i / total_samples)) ** 0.55
            val = 0
            for f in freqs:
                val += math.sin(2 * math.pi * f * t)
            val = (val / len(freqs)) * env * 16000
            samples.append(val)
        return self._create_sound_from_samples(samples)

    def _gen_wrong(self):
        samples = []
        duration = 0.35
        total_samples = int(self.sample_rate * duration)
        for i in range(total_samples):
            t = i / self.sample_rate
            freq = 220 - (t / duration) * 80
            env = 1.0 - (i / total_samples)
            wave = 1.0 if math.sin(2 * math.pi * freq * t) > 0 else -1.0
            val = wave * env * 7500
            samples.append(val)
        return self._create_sound_from_samples(samples)

    def _gen_fanfare(self):
        samples = []
        notes = [(392.0, 0.12), (523.25, 0.12), (659.25, 0.14), (783.99, 0.28)]
        for freq, dur in notes:
            note_samples = int(self.sample_rate * dur)
            for i in range(note_samples):
                t = i / self.sample_rate
                env = (1.0 - (i / note_samples)) ** 0.5
                val = math.sin(2 * math.pi * freq * t) * env * 15000
                samples.append(val)
        chord = [523.25, 659.25, 783.99, 1046.5]
        dur = 0.45
        total = int(self.sample_rate * dur)
        for i in range(total):
            t = i / self.sample_rate
            env = (1.0 - (i / total)) ** 0.7
            val = sum(math.sin(2 * math.pi * f * t) for f in chord) / len(chord)
            samples.append(val * env * 14000)
        return self._create_sound_from_samples(samples)

    def _gen_select(self):
        samples = []
        duration = 0.05
        total_samples = int(self.sample_rate * duration)
        for i in range(total_samples):
            t = i / self.sample_rate
            freq = 880 - (t / duration) * 220
            env = 1.0 - (i / total_samples)
            val = math.sin(2 * math.pi * freq * t) * env * 7000
            samples.append(val)
        return self._create_sound_from_samples(samples)

    def _gen_levelup(self):
        samples = []
        notes = [(523.25, 0.09), (659.25, 0.09), (783.99, 0.09), (1046.5, 0.18)]
        for freq, dur in notes:
            n = int(self.sample_rate * dur)
            for i in range(n):
                t = i / self.sample_rate
                env = (1.0 - (i / n)) ** 0.4
                val = math.sin(2 * math.pi * freq * t) * env * 14000
                samples.append(val)
        return self._create_sound_from_samples(samples)

    def _gen_ending_music(self):
        """Música 8-bit simples em loop para a tela final."""
        samples = []
        # melodia alegre (C major-ish), onda quadrada suave + baixo simples
        melody = [
            (523.25, 0.18), (659.25, 0.18), (783.99, 0.18), (659.25, 0.18),
            (523.25, 0.18), (587.33, 0.18), (659.25, 0.36),
            (587.33, 0.18), (659.25, 0.18), (698.46, 0.18), (783.99, 0.18),
            (659.25, 0.18), (523.25, 0.18), (587.33, 0.36),
            (392.00, 0.18), (523.25, 0.18), (659.25, 0.18), (783.99, 0.18),
            (880.00, 0.18), (783.99, 0.18), (659.25, 0.36),
            (523.25, 0.18), (587.33, 0.18), (659.25, 0.18), (523.25, 0.18),
            (587.33, 0.18), (392.00, 0.18), (523.25, 0.36),
        ]
        bass = [130.81, 164.81, 196.00, 174.61]
        for idx, (freq, dur) in enumerate(melody):
            n = int(self.sample_rate * dur)
            bfreq = bass[(idx // 2) % len(bass)]
            for i in range(n):
                t = i / self.sample_rate
                env = 0.9
                # pequeno envelope por nota
                if i < 120:
                    env *= i / 120.0
                elif i > n - 240:
                    env *= max(0.0, (n - i) / 240.0)
                sq = 1.0 if math.sin(2 * math.pi * freq * t) >= 0 else -0.8
                tri = math.sin(2 * math.pi * bfreq * t)
                val = (sq * 0.55 + tri * 0.25) * env * 9000
                samples.append(val)
        return self._create_sound_from_samples(samples)

    def play(self, name):
        """Toca o efeito sonoro pelo nome."""
        if not self.enabled:
            return
        sound = self.sounds.get(name)
        if sound:
            sound.play()

    def play_music(self, name, loops=-1):
        if not self.enabled:
            return
        if self.current_music == name and self.music_channel and self.music_channel.get_busy():
            return
        sound = self.sounds.get(name)
        if not sound:
            return
        self.stop_music()
        self.music_channel = sound.play(loops=loops)
        self.current_music = name

    def stop_music(self):
        if not self.enabled:
            return
        try:
            if self.music_channel:
                self.music_channel.stop()
        except Exception:
            pass
        self.music_channel = None
        self.current_music = None

sound_manager = SoundManager()
