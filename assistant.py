#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Description: This is the main file for the Computer assistant.
#              It uses Porcupine for keyword detection, Leopard for speech-to-text,
#              OpenAI for chat, and NSSpeechSynthesizer for text-to-speech.
#              It is meant to be run on macOS.
#              It is meant to be run with Python 3.10.
#              It is meant to be run with the following dependencies installed:
#               - pvporcupine
#               - pvleopard
#               - google-generativeai
#               - langchain-google-genai
#               - pyaudio
#               - pyttsx3
#               - struct
#               - wave
#              It is meant to be run after replacing env/lib/python3.10/sites-packages/pyttsx3/drivers/nsss.py with the following file:
#               - nsss.py

import google.generativeai as genai
import os
import pvleopard as pvleopard
import pvporcupine
import pyaudio
import pyttsx3
import struct
import wave


PICO_VOICE_API_KEY = 'REPLACE_WITH_YOUR_API_KEY'
GOOGLE_API_KEY = 'REPLACE_WITH_YOUR_API_KEY'


# Initialize Porcupine API client (for keyword detection)
porcupine = pvporcupine.create(
    access_key= PICO_VOICE_API_KEY,
    keywords=['computer']
)


# Initialize Leopard API client (for speech-to-text)
leopard = pvleopard.create(access_key=PICO_VOICE_API_KEY)


# Initialize Gemini API client
genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel('gemini-pro')


# Initialize text to speech engine
engine = pyttsx3.init('nsss', debug=True)
engine.setProperty('rate', 185)


# Initialize PyAudio
audio = pyaudio.PyAudio()
stream = audio.open(
    rate=porcupine.sample_rate,
    channels=1,
    format=pyaudio.paInt16,
    input=True,
    frames_per_buffer=porcupine.frame_length,
)

# Function to speak text:
#  - text: string to speak
#
# Example usage:
#  speak("Hello world!")
def speak(text):
    engine.say(text)
    engine.runAndWait()


# Function to chat with Gemini:
#  - prompt: string to prompt the AI with
#   (e.g. "What is the meaning of life?")
#
# Example usage:
#  gemini_chat("What is the meaning of life?")
def gemini_chat(prompt):
    generation_config = genai.types.GenerationConfig(max_output_tokens=256, temperature=0.6)
    response = model.generate_content(prompt, generation_config=generation_config)

    return response.text

# Function to record audio:
#  - filename: name of the file to save the audio to
#  - duration: duration of the recording in seconds
#
# Example usage:
#  record_audio("recorded_audio.wav", 5)
def record_audio(filename, duration):
    frames = []

    for _ in range(0, int(porcupine.sample_rate / porcupine.frame_length * duration)):
        audio_data = stream.read(porcupine.frame_length, exception_on_overflow=False)
        audio_frame = struct.unpack_from("h" * porcupine.frame_length, audio_data)
        frames.append(audio_data)

    with wave.open(filename, 'wb') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(audio.get_sample_size(pyaudio.paInt16))
        wf.setframerate(porcupine.sample_rate)
        wf.writeframes(b''.join(frames))

# Function to get the activation word:
#  - returns True if the activation word was detected, False otherwise
#
# Example usage:
#  if get_activation_word():
#      print("Activation word detected!")
def get_activation_word():
    # Read audio data from the microphone
    audio_data = stream.read(porcupine.frame_length, exception_on_overflow=False)
    audio_frame = struct.unpack_from("h" * porcupine.frame_length, audio_data)

    # Process audio frame with Porcupine
    keyword_index = porcupine.process(audio_frame)

    return keyword_index == 0


if __name__ == '__main__':
    try:
        # Saying a welcome message with instructions for the user
        speak("Hello, I'm Computer, your personal assistant. Say my name and ask me anything:")
        print("Listening...")

        # Main loop
        while True:
            if get_activation_word():
                print("Activation word detected! Recording speech...")

                # Record speech for a fixed duration (5 seconds)
                duration_seconds = 5
                audio_file = "recorded_audio.wav"
                record_audio(audio_file, duration_seconds)

                # Transcribe the recorded speech using Leopard
                print("Transcribing speech...")
                transcript, words = leopard.process_file(os.path.abspath(audio_file))
                print("Transcript:", transcript)

                response = gemini_chat(transcript)

                # Print the response
                print(response)

                # Speak the response
                speak(response)

                # Remove the audio file if you don't need it
                os.remove(audio_file)

    finally:
        # Clean up resources
        stream.stop_stream()
        stream.close()
        audio.terminate()
        porcupine.delete()
