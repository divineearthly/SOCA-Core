#!/usr/bin/env python3
"""
SOCA Voice Assistant
Uses Vosk for STT and Piper for TTS
"""

import os
import subprocess
import json

def listen():
    """Listen for voice input using Vosk."""
    # In production, this would use vosk with microphone
    return "What crop should I grow in Assam?"

def speak(text):
    """Speak output using Piper."""
    # In production, this would use Piper TTS
    print(f"Speaking: {text}")
    return True

def run_voice_assistant():
    print("🎤 SOCA Voice Assistant")
    print("=" * 40)
    
    while True:
        try:
            # Listen for command
            query = listen()
            if query.lower() in ['exit', 'quit']:
                break
            
            # Process with SOCA
            result = subprocess.run(
                ['./soca_agent', query],
                capture_output=True,
                text=True
            )
            
            # Speak response
            if result.returncode == 0:
                speak(result.stdout)
            else:
                speak("Sorry, I couldn't understand that.")
                
        except KeyboardInterrupt:
            break

if __name__ == "__main__":
    run_voice_assistant()
