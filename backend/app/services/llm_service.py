from openai import AsyncOpenAI
from app.config import get_settings
from typing import List, Dict
import json

settings = get_settings()

client = AsyncOpenAI(
    api_key=settings.GROQ_API_KEY,
    base_url=settings.LLM_BASE_URL
)

class LLMService:
    @staticmethod
    async def generate_response(
        messages: List[Dict[str, str]], 
        temperature: float = None,
        max_tokens: int = None
    ) -> str:
        """Generate response from LLM with proper error handling"""
        try:
            print(f"🤖 Calling LLM with {len(messages)} messages...")
            print(f"Last message: {messages[-1]['content'][:100]}...")
            
            response = await client.chat.completions.create(
                model=settings.LLM_MODEL,
                messages=messages,
                temperature=temperature or settings.LLM_TEMPERATURE,
                max_tokens=max_tokens or settings.MAX_TOKENS
            )
            
            result = response.choices[0].message.content
            print(f"✅ LLM Response received: {result[:100]}...")
            return result
            
        except Exception as e:
            print(f"❌ LLM Error: {type(e).__name__}: {str(e)}")
            # Re-raise the error instead of swallowing it
            raise Exception(f"LLM API Error: {str(e)}")
    
    @staticmethod
    async def classify_persona_semantic(message: str, conversation_history: List[Dict]) -> str:
        """Use LLM to semantically classify user persona"""
        
        # Build conversation summary
        recent_messages = conversation_history[-6:] if len(conversation_history) > 6 else conversation_history
        history_summary = "\n".join([
            f"{'User' if m['role']=='user' else 'Agent'}: {m['content'][:100]}"
            for m in recent_messages
        ])
        
        classification_prompt = f"""Analyze this candidate's communication pattern.

CURRENT MESSAGE: "{message}"

RECENT CONVERSATION:
{history_summary}

CLASSIFY AS ONE OF: confused, efficient, chatty, edge, neutral

Respond with EXACTLY ONE WORD:"""

        messages = [{"role": "user", "content": classification_prompt}]
        
        try:
            response = await LLMService.generate_response(messages, temperature=0.3, max_tokens=10)
            persona = response.strip().lower()
            
            # Validate response
            valid_personas = ["confused", "efficient", "chatty", "edge", "neutral"]
            if persona not in valid_personas:
                for word in response.lower().split():
                    if word in valid_personas:
                        return word
                print(f"⚠️ Invalid persona '{persona}', using fallback")
                return LLMService._fallback_persona_detection(message, conversation_history)
            
            print(f"✅ Persona detected: {persona}")
            return persona
            
        except Exception as e:
            print(f"⚠️ Persona classification failed: {e}, using fallback")
            return LLMService._fallback_persona_detection(message, conversation_history)
    
    @staticmethod
    def _fallback_persona_detection(message: str, history: List[Dict]) -> str:
        """Fallback rule-based detection if LLM fails"""
        message_lower = message.lower()
        word_count = len(message.split())
        
        # Edge case indicators
        edge_keywords = ["joke", "tell me about you", "what's your", "do you", "can you tell"]
        if any(kw in message_lower for kw in edge_keywords):
            return "edge"
        
        # Confused indicators
        confused_keywords = ["not sure", "don't know", "maybe", "i guess", "what do you mean"]
        if sum(1 for kw in confused_keywords if kw in message_lower) >= 2:
            return "confused"
        
        # Efficient (short messages)
        if word_count < 12:
            recent_user = [m for m in history[-4:] if m.get("role") == "user"]
            if len(recent_user) >= 2:
                avg_len = sum(len(m['content'].split()) for m in recent_user) / len(recent_user)
                if avg_len < 15:
                    return "efficient"
        
        # Chatty (long messages)
        if word_count > 80:
            return "chatty"
        
        return "neutral"
    
    @staticmethod
    async def generate_adapted_question(
        role: str,
        persona: str,
        conversation_history: List[Dict],
        asked_questions: List[str]
    ) -> str:
        """Generate persona-adapted interview question"""
        
        # Simple, effective system prompt
        system_prompt = f"""You are conducting a {role} job interview. 

The candidate's communication style is: {persona}

ADAPT YOUR STYLE:
- confused: Be supportive, give examples, break down questions
- efficient: Be direct and concise
- chatty: Be focused, gently redirect if needed
- edge: Be professional but firm in redirecting
- neutral: Be professional and balanced

Generate ONE interview question appropriate for a {role} position.
Make it conversational and natural, not robotic."""

        # Build context from recent conversation
        recent_context = ""
        if conversation_history:
            recent = conversation_history[-4:]
            recent_context = "\n".join([
                f"{'You' if m['role']=='assistant' else 'Candidate'}: {m['content'][:150]}"
                for m in recent
            ])
        
        user_prompt = f"""Recent conversation:
{recent_context if recent_context else "Starting interview"}

Asked before: {len(asked_questions)} questions

Generate your next interview question:"""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        try:
            question = await LLMService.generate_response(messages, temperature=0.8, max_tokens=200)
            return question.strip()
        except Exception as e:
            print(f"❌ Question generation failed: {e}")
            # Fallback to simple question
            return f"Tell me about your experience relevant to this {role} position."
    
    @staticmethod
    async def generate_intelligent_followup(
        role: str,
        previous_question: str,
        user_answer: str,
        persona: str
    ) -> str:
        """Generate contextual follow-up"""
        
        prompt = f"""You asked: "{previous_question}"

They answered: "{user_answer}"

Their communication style: {persona}

Generate ONE natural follow-up question that:
1. Digs deeper into their answer
2. Stays relevant to {role} interview
3. Adapts to their {persona} style

Follow-up question:"""

        messages = [{"role": "user", "content": prompt}]
        
        try:
            followup = await LLMService.generate_response(messages, temperature=0.7, max_tokens=150)
            return followup.strip()
        except Exception as e:
            print(f"❌ Follow-up generation failed: {e}")
            return "Can you tell me more about that?"
