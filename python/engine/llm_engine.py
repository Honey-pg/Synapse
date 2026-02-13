
import ollama
from python.engine.logger import logger
import python.engine.events as events

class LLM_Engine:
    def __init__(self):
        self.history = [ {"role": "system", "content": "You are Sarah, a highly advanced AI. Keep answers short, witty, and helpful."}
            ]
    def chat(self, text, session_id=None):
        self.history.append({"role": "user", "content": text})
        response = ollama.chat(model= 'llama3.1:8b', messages=self.history)
        reply = response['message']['content']
        self.history.append({"role": "assistant", "content": reply})
        
        if session_id:
            logger.log_event(
                event_name=events.PROCESSING,
                event_data={"input": text, "output": reply},
                session_id=session_id
            )
            
        return reply





