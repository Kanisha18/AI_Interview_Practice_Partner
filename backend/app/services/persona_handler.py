from typing import Dict, List

class PersonaHandler:
    PERSONA_INDICATORS = {
        "confused": ["not sure", "don't know", "maybe", "i guess", "kind of"],
        "efficient": [],
        "chatty": [],
        "edge": ["joke", "story", "unrelated", "random"]
    }
    
    @staticmethod
    def detect_persona(message: str, history: List[Dict]) -> str:
        message_lower = message.lower()
        word_count = len(message.split())
        
        recent_messages = [h for h in history[-5:] if h.get("role") == "user"]
        avg_length = sum(len(m.get("content", "").split()) for m in recent_messages) / max(len(recent_messages), 1)
        
        if word_count < 10 and avg_length < 15:
            return "efficient"
        
        confused_count = sum(1 for indicator in PersonaHandler.PERSONA_INDICATORS["confused"] 
                            if indicator in message_lower)
        if confused_count >= 2:
            return "confused"
        
        if word_count > 100:
            return "chatty"
        
        edge_count = sum(1 for indicator in PersonaHandler.PERSONA_INDICATORS["edge"] 
                        if indicator in message_lower)
        if edge_count >= 1:
            return "edge"
        
        return "efficient" #recheck
    
    @staticmethod
    async def adapt_response(response: str, persona: str) -> str:
        adaptations = {
            "confused": "\n\n💡 *Take your time and think it through!*",
            "efficient": "",
            "chatty": "\n\n⏰ *Great! Let's move to the next question.*",
            "edge": "\n\n😊 *Let's refocus on the interview.*"
        }
        return response + adaptations.get(persona, "")
