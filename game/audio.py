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
                "correct": self._gen_chord([523.25, 659.25, 783.99], 0.4), # Dó-Mi-Sol
                "wrong": self._gen_wrong(),
                "fanfare": self._gen_fanfare()
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
        duration = 0.04
        total_samples = int(self.sample_rate * duration)
        for i in range(total_samples):
            t = i / self.sample_rate
            env = (1.0 - (i / total_samples)) ** 2
            val = math.sin(2 * math.pi * 140 * t) * env * 4000
            samples.append(val)
        return self._create_sound_from_samples(samples)

    def _gen_dialog(self):
        samples = []
        duration = 0.06
        total_samples = int(self.sample_rate * duration)
        for i in range(total_samples):
            t = i / self.sample_rate
            freq = 480
            env = math.sin(math.pi * (i / total_samples))
            val = math.sin(2 * math.pi * freq * t) * env * 8000
            samples.append(val)
        return self._create_sound_from_samples(samples)

    def _gen_door(self):
        samples = []
        duration = 0.25
        total_samples = int(self.sample_rate * duration)
        for i in range(total_samples):
            t = i / self.sample_rate
            env = 1.0 - (i / total_samples)
            freq1 = 260
            freq2 = 390
            val = (math.sin(2 * math.pi * freq1 * t) + math.sin(2 * math.pi * freq2 * t)) * 0.5 * env * 14000
            samples.append(val)
        return self._create_sound_from_samples(samples)

    def _gen_chord(self, freqs, duration):
        samples = []
        total_samples = int(self.sample_rate * duration)
        for i in range(total_samples):
            t = i / self.sample_rate
            env = (1.0 - (i / total_samples)) ** 0.6
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
            # Onda quadrada suave para som de erro retrô
            wave = 1.0 if math.sin(2 * math.pi * freq * t) > 0 else -1.0
            val = wave * env * 8000
            samples.append(val)
        return self._create_sound_from_samples(samples)

    def _gen_fanfare(self):
        samples = []
        # Notas da vitória: Sol, Dó, Mi, Sol agudo
        notes = [(392.0, 0.12), (523.25, 0.12), (659.25, 0.14), (783.99, 0.35)]
        for freq, dur in notes:
            note_samples = int(self.sample_rate * dur)
            for i in range(note_samples):
                t = i / self.sample_rate
                env = (1.0 - (i / note_samples)) ** 0.5
                val = math.sin(2 * math.pi * freq * t) * env * 15000
                samples.append(val)
        return self._create_sound_from_samples(samples)

    def play(self, name):
        """Toca o efeito sonoro pelo nome."""
        if not self.enabled:
            return
        sound = self.sounds.get(name)
        if sound:
            sound.play()

sound_manager = SoundManager()
