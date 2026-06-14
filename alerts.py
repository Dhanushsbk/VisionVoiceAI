import sys
import threading
import queue

# Try to import TTS libraries
try:
    import pyttsx3
    import pythoncom
    TTS_AVAILABLE = True
except ImportError:
    TTS_AVAILABLE = False

speech_queue = queue.Queue()
current_speech_rate = 150
rate_lock = threading.Lock()


def set_speech_rate(rate):
    global current_speech_rate
    with rate_lock:
        current_speech_rate = rate


def _speech_worker():
    if not TTS_AVAILABLE:
        return

    pythoncom.CoInitialize()
    try:
        engine = pyttsx3.init()

        while True:
            text = speech_queue.get()
            if text is None:
                break

            try:
                with rate_lock:
                    rate = current_speech_rate

                engine.setProperty("rate", rate)
                engine.say(text)
                engine.runAndWait()

            except Exception as e:
                print("Speech error:", e)

            finally:
                speech_queue.task_done()

    finally:
        pythoncom.CoUninitialize()


if TTS_AVAILABLE:
    worker_thread = threading.Thread(
        target=_speech_worker,
        daemon=True
    )
    worker_thread.start()


def speak_async(text):
    if not text:
        return

    if not TTS_AVAILABLE:
        print("TTS:", text)
        return

    while not speech_queue.empty():
        try:
            speech_queue.get_nowait()
            speech_queue.task_done()
        except:
            break

    speech_queue.put(text)


def play_siren():
    print("🚨 Emergency! Stop!")


def generate_alert(objects):
    if "person" in objects:
        return "Person detected"
    if "car" in objects:
        return "Vehicle nearby"
    return None
