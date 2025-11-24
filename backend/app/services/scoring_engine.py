from typing import List, Dict
from collections import Counter

class ScoringEngine:
    @staticmethod
    async def generate_overall_scores(conversation_history: List[Dict]) -> Dict[str, float]:
        """Generate persona-aware scores with realistic, balanced criteria"""
        
        print(f"📊 Scoring Engine Called")
        print(f"📝 Conversation history entries: {len(conversation_history)}")
        
        if not conversation_history:
            print("⚠️ No conversation history!")
            return {
                "overall": 0.0,
                "logic": 0.0,
                "communication": 0.0,
                "focus": 0.0,
                "persona_adaptivity": 0.0
            }
        
        # Extract user answers
        answers = []
        answer_personas = []
        
        for i, entry in enumerate(conversation_history):
            if entry.get("role") == "user":
                content = entry.get("content", "")
                persona = entry.get("persona_detected", "neutral")
                
                print(f"  📌 User answer {len(answers)+1}: persona='{persona}', length={len(content.split())} words")
                
                answers.append({
                    "content": content,
                    "persona": persona,
                    "length": len(content.split())
                })
                answer_personas.append(persona)
        
        print(f"✅ Found {len(answers)} user answers")
        print(f"✅ Personas: {answer_personas}")
        
        if not answers:
            print("⚠️ No user answers found!")
            return {
                "overall": 0.0,
                "logic": 0.0,
                "communication": 0.0,
                "focus": 0.0,
                "persona_adaptivity": 0.0
            }
        
        # Count personas
        persona_counts = Counter(answer_personas)
        total_answers = len(answers)
        
        print(f"📊 Persona distribution: {dict(persona_counts)}")
        
        # Calculate ratios
        confused_ratio = persona_counts.get("confused", 0) / total_answers
        edge_ratio = persona_counts.get("edge", 0) / total_answers
        chatty_ratio = persona_counts.get("chatty", 0) / total_answers
        efficient_ratio = persona_counts.get("efficient", 0) / total_answers
        
        # --- LOGIC SCORE (More Strict) ---
        # Start at 4.0 (not 5.0), earn points for good answers
        logic_score = 3.0  # Lower starting point
        logic_score += efficient_ratio * 2.0  # Strong reward for efficient
        logic_score -= confused_ratio * 3.0   # Strong penalty for confusion
        logic_score -= edge_ratio * 2.5   
        logic_score = max(0.1, min(5.0, logic_score))  # Floor at 0.1, not 1.0
        
        # --- COMMUNICATION SCORE (More Balanced) ---
        # Start at 2.5, work your way up
        communication_score = 2.0  # Lower starting point
        communication_score += efficient_ratio * 2.5    # Strong reward for efficient
        communication_score -= chatty_ratio * 2.0       # Stronger penalty for rambling
        communication_score -= confused_ratio * 1.0
        communication_score = max(0.1, min(5.0, communication_score))

        # --- FOCUS SCORE (Stricter) ---
        # Start at 3.5, can go up or down
        focus_score = 2.5  # Lower starting point
        focus_score += efficient_ratio * 2.0            # Reward for staying on topic
        focus_score -= edge_ratio * 3.0                 # Heavy penalty for off-topic
        focus_score -= chatty_ratio * 1.5               # Penalty for losing focus
        focus_score -= confused_ratio * 1.2  
        focus_score = max(0.1, min(5.0, focus_score))

        # --- PERSONA ADAPTIVITY (More Nuanced) ---
        unique_personas = len(set(answer_personas))
        if unique_personas == 1:
            if answer_personas[0] in ["confused", "edge"]:
                persona_adaptivity = 1.0  # Stuck in bad persona
            elif answer_personas[0] == "efficient":
                persona_adaptivity = 4.5  # Ideal
            else:  # chatty
                persona_adaptivity = 2.0
        elif unique_personas == 2:
            if "efficient" in answer_personas and \
               ("confused" not in answer_personas and "edge" not in answer_personas):
                persona_adaptivity = 4.2  # Good adaptive range
            else:
                persona_adaptivity = 2.5  # Mixed but includes negatives
        elif unique_personas >= 3:
            bad_count = persona_counts.get("confused", 0) + persona_counts.get("edge", 0)
            if bad_count > total_answers * 0.3:
                persona_adaptivity = 1.5  # Inconsistent with too many negatives
            else:
                persona_adaptivity = 4.0  # Good range without too many negatives
        else:
            persona_adaptivity = 2.0

        persona_adaptivity = max(0.1, min(5.0, persona_adaptivity))

        # --- OVERALL (Weighted Average) ---
        # Give more weight to logic and communication
        overall = (
            logic_score * 0.30 +
            communication_score * 0.30 +
            focus_score * 0.25 +
            persona_adaptivity * 0.15
        )
        overall = round(overall, 1)

        scores = {
            "overall": round(overall, 1),
            "logic": round(logic_score, 1),
            "communication": round(communication_score, 1),
            "focus": round(focus_score, 1),
            "persona_adaptivity": round(persona_adaptivity, 1)
        }

        print(f"🎯 Final scores: {scores}")

        return scores
