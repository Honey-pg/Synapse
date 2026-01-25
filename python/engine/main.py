from python.engine.music_engine import MusicEngine
from stt_engine import STT_Engine
from tts_engine import TTS_Engine
from llm_engine import LLM_Engine
import threading

from vision_pro import Vision_Pro
import colorama
import time

colorama.init(autoreset=True)


class Synapse:
    def __init__(self):
        print(colorama.Fore.CYAN + f"Initializing Synapse AI Engine...")

        self.vision = Vision_Pro()
        self.mouth = TTS_Engine()
        self.ear = STT_Engine()
        self.brain = LLM_Engine()
        self.music = MusicEngine()
        self.mouth.speak("Hi there")

    def check_exit(self, text):
        exit_phrases = ["exit", "quit", "stop", "terminate", "bye", "adios", "chal thik hai", "milte hai"]
        if any(phrase in text.lower() for phrase in exit_phrases):
            return True
        return False

    def start(self):
        while True:
            try:
                # 1. Listen
                command = self.ear.listen()

                # Safety: Agar Sarah khud bol rahi hai to mat suno
                if self.mouth._is_speaking:
                    time.sleep(0.1)
                    continue

                if command:
                    # Har jagah lowercase use karenge matching ke liye
                    command_lower = command.lower()

                    # EXIT CHECK
                    if self.check_exit(command_lower):
                        self.mouth.speak("Goodbye!")
                        break
                    music_triggers = ["play", "bajao", "sunao", "song", "music", "gana"]
                    music_triggers = ["play", "bajao", "sunao", "song", "music", "gana"]

                    # Logic: Agar command me "play" hai (par ye koi question nahi hai)
                    if any(trigger in command_lower for trigger in music_triggers):

                        # 1. Brain se Song Name nikalo
                        # Note: Make sure brain_engine.py me function ka naam 'play_music' hi ho
                        song_name = self.brain.play_music(command_lower)

                        # ... (Music Logic ke andar) ...

                        if song_name and song_name.lower() != "unknown" and song_name.lower() != "none":
                            print(f"🎵 Extracting Song: {song_name}")
                            self.mouth.speak(f"Sure, playing {song_name}.")

                            # 2. Threading Start
                            t = threading.Thread(target=self.music.play, args=(song_name,))
                            t.start()

                            #  Second ka break lo taaki download ho jaye
                            # aur Sarah khud ki awaaz na sune
                            print("[System] Waiting for music to start...")
                            time.sleep(5)

                            continue
                        else:
                            self.mouth.speak("I couldn't understand the song name.")

                        continue
                    # REGISTRATION TRIGGERS
                    # (Sabse pehle check karo agar user naya banda add karna chahta hai)
                    registration_triggers = [
                        "remember this person", "remember him", "remember her",
                        "memorize this face", "register new face", "add a new person",
                        "save this person", "add to memory", "remember me",
                        "learn this face"
                    ]

                    if any(trigger in command_lower for trigger in registration_triggers):
                        print("📝 Switching to Registration Mode...")
                        self.handle_registration_flow()
                        continue  # Loop restart, taaki chat/vision trigger na ho

                    #  VISION TRIGGERS
                    vision_triggers = [
                        "who is this", "who is that", "who is he", "who is she",
                        "who are they", "identify", "identify him", "identify her",
                        "recognize him", "recognize her", "recognize this person",
                        "tell me who this is", "tell me who that is",
                        "who am i", "do you know me", "do you remember me",
                        "what is my name", "verify my identity", "authenticate me",
                        "scan", "scan now", "scan the scene", "scan the room",
                        "what do you see", "what is in front of you",
                        "check camera", "open your eyes", "look at this",
                        "who is in the camera", "who is in the frame",
                        "describe the view", "visual check",
                    ]

                    if any(trigger in command_lower for trigger in vision_triggers):
                        print("📷 Scanning Scene...")
                        detected_people = self.vision.scan_scene()

                        if "Camera Error" in detected_people:
                            self.mouth.speak("My camera is malfunctioning.")
                        elif "Unknown" in detected_people:
                            # Direct registration offer kar sakte ho
                            self.mouth.speak("I see someone, but I don't know them. Do you want me to remember them?")
                            # Yahan logic simple rakha hai filhal
                        else:
                            names_str = ", ".join(detected_people)
                            self.mouth.speak(f"I can see {names_str}.")

                        continue

                    #  DB NAME LOOKUP
                    # Agar user kisi specific bande ka pooch raha hai (e.g. "Who is Ankit?")
                    detected_name_input = self.brain.get_name(command)

                    if detected_name_input:
                        print(f"🔍 Checking DB for input: {detected_name_input}")
                        result = self.vision.get_info(detected_name_input)

                        if result:
                            correct_name, info_data = result
                            natural_sentence = self.brain.generate_info(str(info_data), correct_name)
                            self.mouth.speak(natural_sentence)
                        else:
                            self.mouth.speak(f"I heard {detected_name_input}, but I don't have their details.")

                        continue

                        # := GENERAL CHAT (Fallback)
                    print(f"💬 General Chat: {command}")
                    ai_response = self.brain.chat(command)
                    self.mouth.speak(ai_response)

            except KeyboardInterrupt:
                print("\nStopping Synapse...")
                break

    def handle_registration_flow(self, auto_trigger=False):

        def wait_for_sarah():
            time.sleep(0.5)
            while self.mouth._is_speaking:
                time.sleep(0.1)

        #  CONTEXT CHECK (Unknown Face Trigger)
        if auto_trigger:
            self.mouth.speak("I see someone new. Do you want me to remember them?")
            wait_for_sarah()

            # Jab tak Haan/Na nahi milta, yahi rukenge
            print("[System] Waiting for User Decision (Yes/No)...")
            decision_made = False

            # 3 Attempts denge user ko
            for _ in range(3):
                response = self.ear.listen()

                if not response:
                    continue  # Kuch nahi suna, fir se suno

                if any(w in response.lower() for w in ["yes", "haan", "yep", "sure", "ok"]):
                    decision_made = True
                    break
                elif any(w in response.lower() for w in ["no", "nah", "nahi", "cancel"]):
                    self.mouth.speak("Okay, ignoring.")
                    return  # Exit function

            # Agar 3 baar sunne ke baad bhi koi jawab nahi
            if not decision_made:
                self.mouth.speak("No response. Ignoring for now.")
                return

        # NAME GATHERING
        self.mouth.speak("Okay, tell me their name.")
        wait_for_sarah()

        final_name = None
        final_info = ""
        attempts = 0

        while attempts < 3:
            print(f"[System] Listening for Name (Attempt {attempts + 1})...")
            user_input = self.ear.listen()

            if not user_input:
                self.mouth.speak("I didn't hear anything. Please say the name.")
                wait_for_sarah()
                continue

            if "cancel" in user_input.lower():
                self.mouth.speak("Registration cancelled.")
                return

            # Brain se Name extract karo
            person_data = self.brain.process_name_info(user_input)
            extracted_name = person_data.get("name", user_input)
            extracted_info = person_data.get("info", "")

            if extracted_name == "Unknown":
                self.mouth.speak("I couldn't understand the name. Please try again.")
                wait_for_sarah()
                continue

            # SMART CONFIRMATION
            self.mouth.speak(f"I heard {extracted_name}. Is that correct?")
            wait_for_sarah()

            confirm = self.ear.listen()

            if confirm and any(w in confirm.lower() for w in ["yes", "haan", "sahi", "right", "correct"]):
                final_name = extracted_name
                if len(extracted_info) > 2:
                    final_info = extracted_info
                break
            else:
                self.mouth.speak("Sorry. Please say the name again.")
                wait_for_sarah()

            attempts += 1

        if not final_name:
            self.mouth.speak("I am struggling to hear. Let's try later.")
            return

        # EXISTING USER CHECK (Ye Naya Logic Hai)
        # Vision engine se poocho kya ye banda pehle se hai?
        existing_info = self.vision.check_person_exists(final_name)

        if existing_info:
            current_details = existing_info.get("details", "No details provided")
            self.mouth.speak(f"Wait, I already know {final_name}. You told me: {current_details}.")
            wait_for_sarah()

            self.mouth.speak("Do you want to update this information?")
            wait_for_sarah()

            update_response = self.ear.listen()

            # Agar user bole "Yes" ya "Update"
            if update_response and any(w in update_response.lower() for w in ["yes", "haan", "update", "change"]):
                self.mouth.speak(f"Okay, tell me, who is {final_name} now?")
                wait_for_sarah()

                new_details = self.ear.listen()
                if new_details:
                    new_info_dict = {"details": new_details, "added_on": time.strftime("%Y-%m-%d"), "updated": True}

                    # DB Update Call
                    if self.vision.update_person_info(final_name, new_info_dict):
                        self.mouth.speak(f"Done. I have updated the information for {final_name}.")
                    else:
                        self.mouth.speak("Failed to update database.")
                else:
                    self.mouth.speak("I didn't hear anything. Keeping old info.")
            else:
                self.mouth.speak("Okay, keeping the existing information.")

            return  # (Photo lene ki zaroorat nahi hai)

        # MANDATORY INFO (Sirf New Users Ke Liye)
        if len(final_info) < 5:
            self.mouth.speak(
                f"Got it, {final_name}. Now, tell me, who is he? What do you want me to remember about him?")
            wait_for_sarah()

            details_input = self.ear.listen()

            if details_input and len(details_input) > 2:
                final_info = details_input
            else:
                final_info = "Just a friend."  # Fallback default
                self.mouth.speak("Okay, I'll just remember him as a friend.")
                wait_for_sarah()

        # STEP 5: VISION REGISTRATION (Photo Session)
        self.mouth.speak(f"Registering {final_name}. Look at the camera.")
        wait_for_sarah()

        ret, frame = self.vision.cap.read()
        if ret:
            info_dict = {"details": final_info, "added_on": time.strftime("%Y-%m-%d")}
            success = self.vision.register_face(frame, final_name, info_dict, self.mouth)

            if not success:
                self.mouth.speak("Face capture failed.")
        else:
            self.mouth.speak("Camera error.")


if __name__ == "__main__":
    try:
        app = Synapse()
        app.start()
    except KeyboardInterrupt:
        print(f"Interrupted by user")
