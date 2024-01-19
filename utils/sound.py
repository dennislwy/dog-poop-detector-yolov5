from playsound import playsound

def play_audio_file(file_path):
    playsound(file_path)


if __name__ == "__main__":
    play_audio_file("sounds/police.wav")
