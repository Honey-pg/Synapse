import time
import random
import sys
import os

# Ensure we can import modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from python.engine.logger import logger, get_session_id
import python.engine.events as events

def simulate_interaction():
    session_id = get_session_id()
    print(f"Starting session: {session_id}")

    # 1. STT REQUEST
    logger.log_event(
        event_name=events.STT_REQUEST,
        event_data={"device": "microphone_1"},
        session_id=session_id
    )
    time.sleep(0.5)

    # 2. STT RESPONSE
    recognized_text = "What is the weather today?"
    logger.log_event(
        event_name=events.STT_RESPONSE,
        event_data={"text": recognized_text, "confidence": 0.95},
        session_id=session_id
    )
    time.sleep(0.2)

    # 3. PROCESSING
    logger.log_event(
        event_name=events.PROCESSING,
        event_data={"input": recognized_text, "intent": "weather_query"},
        session_id=session_id
    )
    time.sleep(0.5)

    # 4. TTS REQUEST
    response_text = "The weather is sunny and 25 degrees."
    logger.log_event(
        event_name=events.TTS_REQUEST,
        event_data={"text": response_text},
        session_id=session_id
    )
    time.sleep(0.5)

    # 5. TTS RESPONSE
    if random.random() > 0.1:
        logger.log_event(
            event_name=events.TTS_RESPONSE,
            event_data={"status": "success", "duration_ms": 1500},
            session_id=session_id
        )
    else:
        logger.log_event(
            event_name=events.TTS_ERROR,
            event_data={"error": "Audio device busy"},
            session_id=session_id,
            level="ERROR"
        )

    print("Session complete. Check app.log for details.")

if __name__ == "__main__":
    # Simulate 3 interactions
    for _ in range(3):
        simulate_interaction()
        time.sleep(1)
