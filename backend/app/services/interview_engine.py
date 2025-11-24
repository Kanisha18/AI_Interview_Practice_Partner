from typing import Dict, List
from app.services.llm_service import LLMService
import random

class InterviewEngine:
    ROLE_QUESTIONS = {
        "engineer": [
            "Tell me about a challenging technical problem you've solved recently.",
            "How do you approach debugging a complex system issue?",
            "Describe your experience with software development."
        ],
        "sales": [
            "Tell me about your most successful sales experience.",
            "How do you handle objections from potential clients?",
            "Describe your approach to building relationships."
        ],
        "retail": [
            "Describe a time you provided excellent customer service.",
            "How do you handle difficult customers?",
            "Tell me about working in a fast-paced environment."
        ]
    }
    
    OPENING_QUESTIONS = {
        "engineer": "Let's start! Tell me about your background and what interests you about this engineering role.",
        "sales": "Great to meet you! Tell me about your sales experience.",
        "retail": "Thanks for coming in! Tell me about yourself."
    }
    
    @staticmethod
    def get_opening_question(role: str) -> str:
        return InterviewEngine.OPENING_QUESTIONS.get(role, "Tell me about yourself.")
    
    @staticmethod
    def get_next_question(role: str, asked_questions: List[str]) -> str:
        available = [q for q in InterviewEngine.ROLE_QUESTIONS.get(role, []) 
                    if q not in asked_questions]
        if not available:
            return "Do you have any questions for me?"
        return random.choice(available)
    
    @staticmethod
    async def generate_contextual_followup(role: str, question: str, answer: str, persona: str) -> Dict[str, str]:
        system_prompt = f"You are interviewing for a {role} position. Generate ONE follow-up question based on: {answer}"
        followup = await LLMService.generate_response([{"role": "system", "content": system_prompt}], temperature=0.8)
        return {"type": "followup", "question": followup.strip()}
