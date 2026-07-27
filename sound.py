import pygame
import numpy as np


class SoundManager:
    def __init__(self):
        self.enabled = True
        self.sounds = {}
        self.music_playing = False
        try:
            pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
            self._generate_sounds()
        except Exception:
            self.enabled = False

    def _generate_sounds(self):
        self.sounds['pistol'] = self._generate_tone(200, 0.1, 'noise', volume=0.3)
        self.sounds['shotgun'] = self._generate_tone(150, 0.2, 'noise', volume=0.4)
        self.sounds['chaingun'] = self._generate_tone(250, 0.05, 'noise', volume=0.25)
        self.sounds['chainsaw'] = self._generate_tone(100, 0.15, 'sawtooth', volume=0.3)
        self.sounds['player_hurt'] = self._generate_tone(180, 0.15, 'square', volume=0.2)
        self.sounds['door'] = self._generate_tone(80, 0.4, 'sawtooth', volume=0.15)
        self.sounds['pickup'] = self._generate_tone(600, 0.15, 'sine', volume=0.2)
        self.sounds['weapon_pickup'] = self._generate_tone(800, 0.2, 'sine', volume=0.25)
        self.sounds['no_ammo'] = self._generate_tone(100, 0.1, 'square', volume=0.15)

        self.sounds['imp_alert'] = self._generate_tone(400, 0.2, 'sawtooth', volume=0.2)
        self.sounds['imp_pain'] = self._generate_tone(500, 0.12, 'square', volume=0.18)
        self.sounds['imp_die'] = self._generate_descending(600, 150, 0.4, 'sawtooth', volume=0.25)
        self.sounds['imp_attack'] = self._generate_tone(300, 0.08, 'noise', volume=0.2)

        self.sounds['demon_alert'] = self._generate_tone(150, 0.25, 'sawtooth', volume=0.25)
        self.sounds['demon_pain'] = self._generate_tone(350, 0.1, 'square', volume=0.2)
        self.sounds['demon_die'] = self._generate_descending(400, 80, 0.5, 'sawtooth', volume=0.3)
        self.sounds['demon_attack'] = self._generate_tone(120, 0.12, 'noise', volume=0.3)

        self.sounds['baron_alert'] = self._generate_tone(100, 0.35, 'sawtooth', volume=0.3)
        self.sounds['baron_pain'] = self._generate_tone(250, 0.15, 'square', volume=0.22)
        self.sounds['baron_die'] = self._generate_descending(300, 50, 0.7, 'sawtooth', volume=0.35)
        self.sounds['baron_attack'] = self._generate_tone(200, 0.15, 'noise', volume=0.3)

    def _generate_tone(self, freq, duration, wave_type='sine', volume=0.3):
        sample_rate = 22050
        n_samples = int(sample_rate * duration)
        t = np.linspace(0, duration, n_samples, dtype=np.float32)

        if wave_type == 'sine':
            wave = np.sin(2 * np.pi * freq * t)
        elif wave_type == 'square':
            wave = np.sign(np.sin(2 * np.pi * freq * t))
        elif wave_type == 'sawtooth':
            wave = 2 * (t * freq - np.floor(t * freq + 0.5))
        elif wave_type == 'noise':
            wave = np.random.uniform(-1, 1, n_samples)
        else:
            wave = np.sin(2 * np.pi * freq * t)

        envelope = np.ones_like(wave)
        fade_samples = min(int(sample_rate * 0.01), n_samples)
        envelope[:fade_samples] = np.linspace(0, 1, fade_samples)
        envelope[-fade_samples:] = np.linspace(1, 0, fade_samples)

        wave = wave * envelope * volume
        wave = np.clip(wave, -1, 1)

        sound_array = (wave * 32767).astype(np.int16)
        stereo = np.zeros((n_samples, 2), dtype=np.int16)
        stereo[:, 0] = sound_array
        stereo[:, 1] = sound_array

        return pygame.sndarray.make_sound(stereo)

    def _generate_descending(self, freq_start, freq_end, duration, wave_type='sine', volume=0.3):
        sample_rate = 22050
        n_samples = int(sample_rate * duration)
        t = np.linspace(0, duration, n_samples, dtype=np.float32)
        freqs = np.linspace(freq_start, freq_end, n_samples, dtype=np.float32)

        if wave_type == 'sine':
            wave = np.sin(2 * np.pi * freqs * t)
        elif wave_type == 'square':
            wave = np.sign(np.sin(2 * np.pi * freqs * t))
        elif wave_type == 'sawtooth':
            wave = 2 * (t * freqs - np.floor(t * freqs + 0.5))
        elif wave_type == 'noise':
            wave = np.random.uniform(-1, 1, n_samples)
        else:
            wave = np.sin(2 * np.pi * freqs * t)

        envelope = np.ones_like(wave)
        fade_samples = min(int(sample_rate * 0.01), n_samples)
        envelope[:fade_samples] = np.linspace(0, 1, fade_samples)
        envelope[-fade_samples:] = np.linspace(1, 0, fade_samples)

        wave = wave * envelope * volume
        wave = np.clip(wave, -1, 1)

        sound_array = (wave * 32767).astype(np.int16)
        stereo = np.zeros((n_samples, 2), dtype=np.int16)
        stereo[:, 0] = sound_array
        stereo[:, 1] = sound_array

        return pygame.sndarray.make_sound(stereo)

    def play(self, sound_name):
        if not self.enabled:
            return
        sound = self.sounds.get(sound_name)
        if sound:
            try:
                sound.play()
            except Exception:
                pass

    def play_weapon(self, weapon_name):
        self.play(weapon_name)

    def play_enemy_sound(self, enemy_type, event):
        self.play(f'{enemy_type}_{event}')
