import wave
import pyaudio

def play_audio_file(file_path):
    chunk = 1024  # Buffer size
    wf = wave.open(file_path, 'rb')
    pa = pyaudio.PyAudio()

    # Open the audio stream
    stream = pa.open(format=pa.get_format_from_width(wf.getsampwidth()),
                     channels=wf.getnchannels(),
                     rate=wf.getframerate(),
                     output=True)

    # Read data in chunks and play it
    data = wf.readframes(chunk)
    while data:
        stream.write(data)
        data = wf.readframes(chunk)

    # Close the stream
    stream.close()
    pa.terminate()
