
from stt_engine import STT_Engine
from tts_engine import TTS_Engine
from llm_engine import LLM_Engine
import colorama

colorama.init(autoreset=True)

class Synapse :
    def __init__(self):
        print(colorama.Fore.CYAN + f"Initializing Synapse AI Engine...")

        self.ear = STT_Engine()
        self.mouth  = TTS_Engine()
        self.brain = LLM_Engine()
        self.mouth.speak("System Online. Ready for commands, hi my name is sarah how may I help you")


    def check_exit(self, text):
        exit_phrases = ["exit", "quit", "stop", "terminate", "bye", "adios"]
        if any(phrase in text.lower() for phrase in exit_phrases):
            return True
        return False

    def start(self) :
        while True :
            command = self.ear.listen()
            if command :
                if self.check_exit(command): 
                    self.mouth.speak("Goodbye, see you latter !")
                    break;
                ai_response = self.brain.chat(command)
                self.mouth.speak(ai_response)

if __name__ == "__main__" :
    try :
        app = Synapse()
        app.start()
    except KeyboardInterrupt:
        print(f"Interuppted by user")
