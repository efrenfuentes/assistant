import pvporcupine
import pyaudio
import struct

porcupine = pvporcupine.create(
    access_key='<API_KEY>',
    keywords=['jarvis', 'computer', 'bumblebee', 'terminator']
)

# Initialize PyAudio
audio = pyaudio.PyAudio()
stream = audio.open(
    rate=porcupine.sample_rate,
    channels=1,
    format=pyaudio.paInt16,
    input=True,
    frames_per_buffer=porcupine.frame_length,
)

# Main loop
print("Listening for keywords...")
try:
    while True:
        # Read audio data from the microphone
        audio_data = stream.read(porcupine.frame_length)
        audio_frame = struct.unpack_from("h" * porcupine.frame_length, audio_data)

        # Process audio frame with Porcupine
        keyword_index = porcupine.process(audio_frame)

        if keyword_index == 0:
            print("Keyword 0 detected!")
        elif keyword_index == 1:
            print("Keyword 1 detected!")
        elif keyword_index == 2:
            print("Keyword 2 detected!")
        elif keyword_index == 3:
            print("Keyword 3 detected!")
finally:
    # Clean up resources
    stream.stop_stream()
    stream.close()
    audio.terminate()
    porcupine.delete()
