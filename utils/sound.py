import pygame

pygame_init = False

def play_audio_file(file_path):
    global pygame_init

    if not pygame_init:
        pygame.mixer.init()
        pygame_init = True

    pygame.mixer.Sound(file_path).play()
    # pygame.mixer.quit()
