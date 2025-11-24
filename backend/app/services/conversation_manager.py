from typing import Dict, List
from app.models.session import InterviewSession
from app.services.llm_service import LLMService
from app.services.scoring_engine import ScoringEngine
from app.services.feedback_generator import FeedbackGenerator
from datetime import datetime

class ConversationManager:
    def __init__(self, session: InterviewSession):
        self.session = session
        self.conversation_history = session.conversation_history or []
        self.asked_questions = []
        self.current_persona = session.persona or "neutral"
        self.persona_history = []
        self.max_questions = 6
        self.question_count = session.current_question_index or 0

    async def start_interview(self) -> Dict:
        try:
            opening = await LLMService.generate_adapted_question(
                role=self.session.role,
                persona="neutral",
                conversation_history=[],
                asked_questions=[]
            )
            self.conversation_history.append({
                "role": "assistant",
                "content": opening,
                "timestamp": datetime.utcnow().isoformat(),
                "persona_adapted": "neutral"
            })
            self.asked_questions.append(opening)
            self.question_count = 1
            self.session.current_question_index = 1
            self.session.conversation_history = self.conversation_history
            
            return {
                "message": opening,
                "type": "question",
                "question_number": 1,
                "persona_detected": "neutral",
                "should_continue": True,
                "interview_complete": False
            }
        except Exception as e:
            print(f"❌ Error starting interview: {e}")
            import traceback
            traceback.print_exc()
            raise

    async def process_user_response(self, user_message: str) -> Dict:
        detected_persona = self.current_persona
        
        try:
            detected_persona = await LLMService.classify_persona_semantic(
                user_message,
                self.conversation_history
            )
            print(f"✅ Persona detected: {detected_persona}")
        except Exception as e:
            print(f"⚠️ Persona detection failed: {e}, using current: {self.current_persona}")
            detected_persona = self.current_persona
        
        try:
            self.conversation_history.append({
                "role": "user",
                "content": user_message,
                "timestamp": datetime.utcnow().isoformat(),
                "persona_detected": detected_persona
            })
            
            if detected_persona != self.current_persona:
                self.persona_history.append({
                    "from": self.current_persona,
                    "to": detected_persona,
                    "at_message": len(self.conversation_history)
                })
                self.current_persona = detected_persona
                self.session.persona = detected_persona
            
            self.session.conversation_history = self.conversation_history
            
            questions_asked = self.question_count
            print(f"📊 Questions asked: {questions_asked}/{self.max_questions}")
            
            if questions_asked >= self.max_questions:
                print("🏁 Max questions reached, concluding...")
                return await self.conclude_interview()
            
            next_question = await LLMService.generate_adapted_question(
                role=self.session.role,
                persona=self.current_persona,
                conversation_history=self.conversation_history,
                asked_questions=self.asked_questions
            )
            
            self.conversation_history.append({
                "role": "assistant",
                "content": next_question,
                "timestamp": datetime.utcnow().isoformat(),
                "type": "main",
                "persona_adapted": self.current_persona
            })
            
            self.asked_questions.append(next_question)
            self.question_count += 1
            self.session.current_question_index = self.question_count
            self.session.conversation_history = self.conversation_history
            
            print(f"✅ Generated question {self.question_count}")
            
            return {
                "message": next_question,
                "type": "question",
                "question_number": self.question_count,
                "persona_detected": self.current_persona,
                "should_continue": self.question_count < self.max_questions,
                "interview_complete": False
            }
            
        except Exception as e:
            print(f"❌ Error processing response: {e}")
            import traceback
            traceback.print_exc()
            
            return {
                "message": "I encountered an error. Let's continue.",
                "type": "error",
                "question_number": self.question_count,
                "persona_detected": detected_persona,
                "should_continue": True,
                "interview_complete": False
            }

    async def conclude_interview(self) -> Dict:
        try:
            print("🏁 Concluding interview...")
            print(f"Conversation history length: {len(self.conversation_history)}")
            
            scores = await ScoringEngine.generate_overall_scores(self.conversation_history)
            print(f"✅ Scores: {scores}")
            
            feedback = await FeedbackGenerator.generate_feedback(
                self.session.role,
                self.conversation_history,
                scores
            )
            print(f"✅ Feedback generated")
            
            self.session.scores = scores
            self.session.feedback = feedback
            self.session.status = "completed"
            self.session.completed_at = datetime.utcnow()
            
            concluding_message = (
                f"Thank you for completing this mock interview!\n\n"
                f"🎯 **Overall Performance:** {scores.get('overall', 0):.1f}/5.0\n\n"
                f"Your feedback report is ready."
            )
            
            self.conversation_history.append({
                "role": "assistant",
                "content": concluding_message,
                "timestamp": datetime.utcnow().isoformat(),
                "type": "conclusion"
            })
            
            self.session.conversation_history = self.conversation_history
            
            return {
                "message": concluding_message,
                "type": "conclusion",
                "question_number": self.question_count,
                "scores": scores,
                "feedback": feedback,
                "persona_history": self.persona_history,
                "interview_complete": True
            }
            
        except Exception as e:
            print(f"❌ Error concluding: {e}")
            import traceback
            traceback.print_exc()
            
            return {
                "message": "Thank you for completing the interview!",
                "type": "conclusion",
                "question_number": self.question_count,
                "scores": {"overall": 3.0, "logic": 3.0, "communication": 3.0, "focus": 3.0, "persona_adaptivity": 3.0},
                "feedback": {
                    "overall_impression": "Interview completed.",
                    "strengths": ["Completed all questions"],
                    "areas_for_improvement": [],
                    "next_steps": ["Keep practicing"],
                    "example_strong_response": "Use STAR method.",
                    "scores": {"overall": 3.0},
                    "persona": "neutral"
                },
                "interview_complete": True
            }
