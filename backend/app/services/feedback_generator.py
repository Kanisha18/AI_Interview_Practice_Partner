from typing import Dict, List
from app.services.llm_service import LLMService
from collections import Counter

class FeedbackGenerator:
    """Generate detailed, persona-aware feedback"""
    
    @staticmethod
    async def generate_feedback(
        role: str,
        conversation_history: List[Dict],
        scores: Dict[str, float]
    ) -> Dict:
        """Generate comprehensive feedback based on persona analysis"""
        
        # Extract answers with personas
        answers = []
        answer_personas = []
        
        for i, entry in enumerate(conversation_history):
            if entry.get("role") == "user":
                content = entry.get("content", "")
                persona = entry.get("persona_detected", "efficient")
                if not persona and i > 0:
                    persona = conversation_history[i-1].get("persona_adapted", "efficient")

                question = ""
                if i > 0 and conversation_history[i-1].get("role") == "assistant":
                    question = conversation_history[i-1].get("content", "")
                
                answers.append({
                    "content": content,
                    "persona": persona,
                    "question": question[:80] + "..." if len(question) > 80 else question
                })
                answer_personas.append(persona)
        
        if not answers:
            return FeedbackGenerator._fallback_feedback(scores)
        
        # Persona analysis
        persona_counts = Counter(answer_personas)
        most_common_persona = persona_counts.most_common(1)[0][0] if persona_counts else 'efficient' #recheck
        unique_personas = len(set(answer_personas))
        
        # Build overall impression
        persona_feedback = FeedbackGenerator._get_persona_feedback(
            most_common_persona, 
            unique_personas,
            len(answers)
        )
        
        # Build strengths
        strengths = FeedbackGenerator._get_strengths(persona_counts, answer_personas)
        
        # Build areas for improvement
        areas = FeedbackGenerator._get_improvement_areas(answers, persona_counts)
        
        # Next steps
        next_steps = [
            f"Review the feedback for your {most_common_persona} communication style",
            "Practice varying your response style based on question type",
            "Use STAR method (Situation, Task, Action, Result) for behavioral questions",
            "Record yourself answering questions to identify patterns"
        ]
        
        # Example strong response
        example = (
            "For behavioral questions, use STAR format: "
            "'In my previous role [Situation], I was tasked with [Task]. "
            "I approached this by [Action], which resulted in [Result] - "
            "a 30% improvement in team productivity.'"
        )
        
        return {
            "overall_impression": persona_feedback,
            "strengths": strengths,
            "areas_for_improvement": areas,
            "next_steps": next_steps,
            "example_strong_response": example,
            "scores": scores,
            "persona": most_common_persona
        }
    
    @staticmethod
    def _get_persona_feedback(persona: str, unique_count: int, total_answers: int) -> str:
        """Generate persona-specific feedback"""
        base = f"You demonstrated a '{persona}' communication style throughout the interview. "
        
        persona_insights = {
            "confused": (
                "You frequently hesitated or needed clarification. "
                "This suggests uncertainty - next time, pause to gather your thoughts "
                "before answering, and don't be afraid to ask ONE clarifying question if needed."
            ),
            #recheck
            "efficient": (
                "You answered concisely, directly, and with focus. "
                "This is the ideal communication style for interviews. "
                "Your responses were clear, on-topic, and demonstrated strong time management."
            ),
            "chatty": (
                "You provided rich details and context, which shows enthusiasm. "
                "However, some responses became lengthy and lost focus. "
                "Practice the 2-minute rule: make your point in under 2 minutes, "
                "then check if the interviewer wants more detail."
            ),
            "edge": (
                "You sometimes went off-topic or asked questions back to the interviewer. "
                "In real interviews, this can derail the conversation. "
                "Stay focused on demonstrating why you're the right fit for the role."
            )
        }
        
        feedback = base + persona_insights.get(persona, "")
        
        if unique_count > 1:
            feedback += f" You showed {unique_count} different communication styles, which demonstrates adaptability."
        elif unique_count == 1 and total_answers > 3:
            feedback += " You stayed consistent in one communication style - try varying your approach based on question type."
        
        return feedback
    
    @staticmethod
    def _get_strengths(persona_counts: Counter, answer_personas: List[str]) -> List[str]:
        """Identify strengths based on persona distribution"""
        strengths = [
            "Completed all interview questions",
            "Maintained engagement throughout the session"
        ]
        #recheck
        if persona_counts.get("efficient", 0) > 0:
            strengths.append("Demonstrated concise communication (efficient responses)")
        
        if persona_counts.get("chatty", 0) > 0:
            strengths.append("Provided detailed context and examples (thorough responses)")
        
        if len(set(answer_personas)) >= 2:
            strengths.append("Showed communication flexibility across different question types")
        
        return strengths
    
    # @staticmethod
    # def _get_improvement_areas(answers: List[Dict], persona_counts: Counter) -> List[Dict]:
    #     """Generate specific improvement areas with examples"""
    #     areas = []

    #     for answer in answers:
    #     content = answer["content"]
    #     word_count = len(content.split())
        
    #     # Confused persona issues
    #     confused_answers = [a for a in answers if a["persona"] == "confused"]
    #     if confused_answers:
    #         example = confused_answers[0]
    #         areas.append({
    #             "area": "Clarity & Confidence",
    #             "issue": f"Response showed uncertainty: '{example['content'][:60]}...'",
    #             "recommendation": "Structure your thoughts before answering. Start with your main point, then provide supporting details."
    #         })
        
    #     # Chatty persona issues
    #     chatty_answers = [a for a in answers if a["persona"] == "chatty"]
    #     if chatty_answers and len(chatty_answers) >= 2:
    #         example = chatty_answers[0]
    #         areas.append({
    #             "area": "Conciseness",
    #             "issue": f"Long response: '{example['content'][:60]}...'",
    #             "recommendation": "Practice the STAR method to keep answers structured and focused. Aim for 1-2 minutes per response."
    #         })
        
    #     # Edge persona issues
    #     edge_answers = [a for a in answers if a["persona"] == "edge"]
    #     if edge_answers:
    #         example = edge_answers[0]
    #         areas.append({
    #             "area": "Professional Focus",
    #             "issue": f"Off-topic or questioning interviewer: '{example['content'][:60]}...'",
    #             "recommendation": "Stay focused on demonstrating your qualifications. Save your questions for the end of the interview."
    #         })
        
    #     # Efficient persona caution
    #     efficient_count = persona_counts.get("efficient", 0)
    #     if efficient_count >= len(answers) * 0.7:
    #         # areas.append({
    #         #     "area": "Response Depth",
    #         #     "issue": "Most responses were very brief",
    #         #     "recommendation": "While conciseness is good, ensure you're providing enough detail and examples to showcase your experience."
    #         # })
    #         areas.append({
    #             "area": "Consistency",
    #             "issue": "No major weaknesses detected",
    #             "recommendation": "Continue practicing to maintain your strong performance level. Focus on staying calm under pressure."
    #         })
        
    #     # If no issues found
    #     # if not areas:
    #         # areas.append({
    #         #     "area": "Consistency",
    #         #     "issue": "No major weaknesses detected",
    #         #     "recommendation": "Continue practicing to maintain your strong performance level. Focus on staying calm under pressure."
    #         # })
    #     return areas

    @staticmethod
    def _get_improvement_areas(answers: List[Dict], persona_counts: Counter) -> List[Dict]:
        """Generate specific improvement areas with examples"""
        areas = []

        for answer in answers:
            content = answer["content"]
            word_count = len(content.split())
            persona = answer["persona"]

            # Confused persona issues (with word count check)
            if persona == "confused":
                if word_count < 15:
                    areas.append({
                        "area": "Clarity & Confidence",
                        "issue": f"Very brief and uncertain answer: '{content[:60]}...'",
                        "recommendation": "Try to elaborate more and structure your thoughts before answering."
                    })
                else:
                    areas.append({
                        "area": "Clarity & Confidence",
                        "issue": f"Response showed uncertainty: '{content[:60]}...'",
                        "recommendation": "Structure your thoughts before answering. Start with your main point, then provide supporting details."
                    })

            # Chatty persona issues (with word count check)
            if persona == "chatty":
                if word_count > 100:
                    areas.append({
                        "area": "Conciseness",
                        "issue": f"Very long response: '{content[:60]}...'",
                        "recommendation": "Practice summarizing your answer to focus on the main point."
                    })
                elif word_count > 60:
                    areas.append({
                        "area": "Conciseness",
                        "issue": f"Long response: '{content[:60]}...'",
                        "recommendation": "Practice the STAR method to keep answers structured and focused. Aim for 1-2 minutes per response."
                    })

            # Edge persona issues (with word count check, if desired)
            if persona == "edge":
                areas.append({
                    "area": "Professional Focus",
                    "issue": f"Off-topic or questioning interviewer: '{content[:60]}...'",
                    "recommendation": "Stay focused on demonstrating your qualifications. Save your questions for the end of the interview."
                })

            # Efficient persona issues (with word count check)
            if persona == "efficient":
                if word_count < 10:
                    areas.append({
                        "area": "Response Depth",
                        "issue": f"Very brief answer: '{content[:60]}...'",
                        "recommendation": "Try to elaborate with a specific example or more detail."
                    })
                elif word_count < 20:
                    areas.append({
                        "area": "Response Depth",
                        "issue": f"Brief answer: '{content[:60]}...'",
                        "recommendation": "Consider adding a concrete example or more context to strengthen your response."
                    })

        # If most answers are efficient and no major issues found, add a positive note
        efficient_count = persona_counts.get("efficient", 0)
        if efficient_count >= len(answers) * 0.7 and not areas:
            areas.append({
                "area": "Consistency",
                "issue": "No major weaknesses detected",
                "recommendation": "Continue practicing to maintain your strong performance level. Focus on staying calm under pressure."
            })

        return areas

    @staticmethod
    def _fallback_feedback(scores: Dict) -> Dict:
        """Fallback if no answers found"""
        return {
            "overall_impression": "Interview session completed. Continue practicing to build confidence.",
            "strengths": ["Participated in the interview", "Showed willingness to practice"],
            "areas_for_improvement": [{
                "area": "Response Detail",
                "issue": "Limited response data available",
                "recommendation": "Provide more detailed answers in future practice sessions"
            }],
            "next_steps": ["Practice behavioral questions", "Prepare STAR method examples"],
            "example_strong_response": "Use specific examples from your experience with measurable results.",
            "scores": scores,
            "persona": "efficient" #recheck
        }
