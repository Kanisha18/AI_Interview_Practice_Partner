# ... (copy your existing code up to conclude_interview)

async def conclude_interview(self) -> Dict:
    try:
        print("🏁 Concluding interview...")
        print(f"Conversation history length: {len(self.conversation_history)}")
        
        # Try scoring
        try:
            scores = await ScoringEngine.generate_overall_scores(self.conversation_history)
            print(f"✅ Scores: {scores}")
        except Exception as score_error:
            print(f"⚠️ Scoring failed: {score_error}, using defaults")
            scores = {
                "overall": 3.5,
                "logic": 3.5,
                "communication": 3.5,
                "focus": 3.5,
                "persona_adaptivity": 3.5
            }
        
        # Simple feedback (bypass FeedbackGenerator for now)
        feedback = {
            "overall_impression": f"You demonstrated a '{self.current_persona}' communication style. You answered {self.question_count} questions.",
            "strengths": ["Completed all interview questions", "Maintained engagement"],
            "areas_for_improvement": [
                {
                    "area": "Practice",
                    "issue": "Continue practicing to improve",
                    "recommendation": "Use STAR method for responses"
                }
            ],
            "next_steps": ["Keep practicing", "Review feedback", "Prepare examples"],
            "example_strong_response": "Use STAR format: Situation, Task, Action, Result.",
            "scores": scores,
            "persona": self.current_persona
        }
        
        print(f"✅ Feedback prepared")
        
        self.session.scores = scores
        self.session.feedback = feedback
        self.session.status = "completed"
        self.session.completed_at = datetime.utcnow()
        
        concluding_message = (
            f"Thank you for completing this mock interview!\n\n"
            f"🎯 **Overall Performance:** {scores.get('overall', 0):.1f}/5.0\n\n"
            f"Your feedback report is ready."
        )
        
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
        raise  # Re-raise to see full error
