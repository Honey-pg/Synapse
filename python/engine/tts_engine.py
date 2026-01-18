import edge_tts
import pygame
import asyncio
import io

class TTS_Engine:
    def __init__(self):
        # Voice set kar lo (AriaNeural bohot achi hai)
        self.voice = "en-US-AriaNeural"
        
        # Mixer init sirf ek baar hona chahiye
        pygame.mixer.init()

    # Ye function internal use ke liye hai (Start with _)
    async def _generate_audio(self, text):
        communicate = edge_tts.Communicate(text, self.voice)
        audio_data = io.BytesIO()
        
        # RAM me stream karo (No SSD usage)
        async for chunk in communicate.stream():
            if chunk['type'] == 'audio':
                audio_data.write(chunk['data'])
        
        audio_data.seek(0)
        return audio_data

    def speak(self, text):
        print(f"[AI]: {text}") # Terminal me dikhane ke liye
        
        # Async function ko Sync tareeke se call karna
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        # Audio data RAM me mango
        mp3_fp = loop.run_until_complete(self._generate_audio(text))
        
        # Play Audio
        pygame.mixer.music.load(mp3_fp)
        pygame.mixer.music.play()

        # Wait karo jab tak audio khatam na ho (Blocking Call)
        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)

# Testing Section 
if __name__ == "__main__":
    try:
        # Object banao
        tts = TTS_Engine()
        
        # Test karo
        tts.speak("Hello Sir, the TTS engine is now fully operational and corrected.")
        tts.speak("Main Hindi bhi samajh sakti hu agar aap model change karein.")
        
    except KeyboardInterrupt:
        print("\nStopped.")