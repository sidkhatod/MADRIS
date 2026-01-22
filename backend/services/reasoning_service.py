from typing import List, Dict, Any
from core.domain import DecisionSnapshot
from services.llm_service import LLMClient

class ReasoningService:
    def __init__(self, llm_client: LLMClient):
        self.llm = llm_client

    def generate_decision_support(self, 
                                  current_narrative: str, 
                                  similar_snapshots: List[DecisionSnapshot]) -> Dict[str, Any]:
        """
        Uses LLM to compare current narrative with retrieved snapshots.
        """
        
        # Format retrieval context
        snapshots_text = ""
        for i, snap in enumerate(similar_snapshots):
            snapshots_text += f"""
            ---
            Case: {snap.case_study_id} (Window: {snap.inferred_time_window})
            Context: {snap.decision_context}
            Action Taken: {snap.action_taken_narrative}
            Risks: {', '.join(snap.risks_perceived)}
            ---
            """
            
        prompt = f"""
        You are an intelligent decision support assistant.
        
        Current Situation:
        {current_narrative}
        
        Relevant Historical Decision Snapshots:
        {snapshots_text}
        
        Task:
        1. Compare the current situation to these historical moments.
        2. Identify common risk patterns.
        3. Surface historically effective interventions mentioned in these snapshots.
        4. Explicitly state uncertainty.
        
        Do NOT predict the future. Do NOT claim causality. Use phrases like "In similar cases...", "Historical patterns suggest...".
        Provide a cohesive narrative analysis in plain text.
        """
        
        response = self.llm.generate_text(prompt)
        
        return {
            "analysis": response,
            "driving_snapshots": [s.snapshot_id for s in similar_snapshots]
        }
