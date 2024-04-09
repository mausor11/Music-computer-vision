import pygame
import speech_recognition as sr


def load_music(url: str):
    pygame.mixer.music.load(url)


class MusicPlayer:
    def __init__(self):
        pygame.mixer.init()
        self.is_music_playing = False

    def set_music_playing(self, is_music_playing):
        self.is_music_playing = is_music_playing

    def play_music(self, mode: str):
        if mode == 'PLAY':
            if not self.is_music_playing:
                pygame.mixer.music.play()
                self.is_music_playing = True
            else:
                pygame.mixer.music.unpause()
        elif mode == 'PAUSE':
            pygame.mixer.music.pause()
