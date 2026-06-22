import sys
import shutil
import subprocess
import threading
import speech_recognition as sr

class VoiceAssistant:
    """
    Handles speech synthesis (TTS) and speech recognition (STT).
    On Linux, uses CLI-based speech engines (espeak or spd-say) and completely avoids
    importing or initializing pyttsx3 to prevent segmentation faults.
    On non-Linux platforms, uses pyttsx3 which is stable there.
    """
    def __init__(self):
        self.use_cli = False
        self.cli_cmd = None
        self.tts_engine = None
        self.tts_lock = threading.Lock()

        if sys.platform.startswith("linux"):
            # On Linux, try CLI tools to avoid pyttsx3 segfaults
            if shutil.which("espeak"):
                self.use_cli = True
                self.cli_cmd = "espeak"
                print("[VoiceAssistant] Using espeak CLI for TTS on Linux to prevent segmentation faults.")
            elif shutil.which("spd-say"):
                self.use_cli = True
                self.cli_cmd = "spd-say"
                print("[VoiceAssistant] Using spd-say CLI for TTS on Linux to prevent segmentation faults.")
            else:
                print("[VoiceAssistant] No stable CLI TTS engine found on Linux. Voice output is disabled to prevent crashes.")
        else:
            # On non-Linux platforms (Windows, macOS), pyttsx3 is stable
            try:
                import pyttsx3
                self.tts_engine = pyttsx3.init()
                voices = self.tts_engine.getProperty('voices')
                for voice in voices:
                    if 'korean' in voice.name.lower() or 'ko' in voice.languages:
                        self.tts_engine.setProperty('voice', voice.id)
                        break
                self.tts_engine.setProperty('rate', 150)
            except Exception as e:
                print(f"Failed to initialize pyttsx3: {e}. Voice output will be disabled.")
                self.tts_engine = None

    def speak(self, text):
        """
        Asynchronously speak text using either CLI tools or pyttsx3 in a background thread.
        """
        print(f"[TTS]: {text}")
        
        if self.use_cli:
            def _speak_cli():
                try:
                    if self.cli_cmd == "espeak":
                        subprocess.run(["espeak", "-v", "ko", "-s", "150", text], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                    elif self.cli_cmd == "spd-say":
                        subprocess.run(["spd-say", "-l", "ko", "-r", "-10", text], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                except Exception as e:
                    print(f"CLI TTS failed: {e}")
            threading.Thread(target=_speak_cli, daemon=True).start()
            return

        if not self.tts_engine:
            return

        def _speak():
            with self.tts_lock:
                try:
                    import pyttsx3
                    local_engine = pyttsx3.init()
                    voices = local_engine.getProperty('voices')
                    for voice in voices:
                        if 'korean' in voice.name.lower() or 'ko' in voice.languages:
                            local_engine.setProperty('voice', voice.id)
                            break
                    local_engine.setProperty('rate', 150)
                    local_engine.say(text)
                    local_engine.runAndWait()
                except Exception as ex:
                    print(f"Error during TTS playback: {ex}")

        threading.Thread(target=_speak, daemon=True).start()

    def listen_from_mic(self, callback):
        """
        Listens to microphone in a separate thread.
        Triggers `callback(text)` when finished, or `callback(None, error_msg)` on failure.
        """
        def _listen():
            recognizer = sr.Recognizer()
            try:
                with sr.Microphone() as source:
                    # Adjust for ambient noise
                    recognizer.adjust_for_ambient_noise(source, duration=1.0)
                    print("[STT]: Listening...")
                    audio = recognizer.listen(source, timeout=5.0, phrase_time_limit=5.0)
                
                print("[STT]: Processing audio...")
                # Recognize speech using Google Web Speech API (free, no API key needed for basic usage)
                text = recognizer.recognize_google(audio, language='ko-KR')
                print(f"[STT] Heard: {text}")
                callback(text, None)
            except sr.RequestError as re:
                callback(None, f"인터넷 연결이 필요합니다: {re}")
            except sr.UnknownValueError:
                callback(None, "무슨 말씀인지 잘 알아듣지 못했어요. 다시 말씀해주세요.")
            except sr.WaitTimeoutError:
                callback(None, "듣기 제한 시간이 초과되었습니다. 다시 시도해주세요.")
            except Exception as e:
                callback(None, f"마이크 장치 오류가 발생했습니다: {str(e)}")

        threading.Thread(target=_listen, daemon=True).start()
