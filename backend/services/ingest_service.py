import json
from typing import List
from core.domain import DecisionSnapshot
from services.llm_service import LLMClient

class IngestService:
    def __init__(self, llm_client: LLMClient):
        self.llm = llm_client

    def processed_case_study(self, case_text: str, source_id: str, case_id: str) -> List[DecisionSnapshot]:
        """
        Chunk text and ask LLM to extract Decision Snapshots.
        """
        # In a real system, we'd chunk large PDFs. Here we assume text fits in context.
        # Improve prompt for Llama 3
        prompt = f"""
        Analyze the following disaster case study text. 
        Extract discrete 'Decision Snapshots' - moments where key decisions were made or considered.
        Capture the uncertainty and context of that specific moment. 
        Do NOT include future knowledge or outcomes.
        
        Text:
        {case_text[:4000]}... (truncated)
        
        RETURN JSON ONLY. Do not write introductory text.
        Return a JSON list of objects with fields: 
        inferred_time_window, location_context, decision_context, uncertainties, risks_perceived, actions_considered, action_taken_narrative.
        """
        
        response = self.llm.generate_text(prompt, system_prompt="You are an expert disaster analyst. Output valid JSON only.")
        
        # Parse logic
        try:
            # Flexible parsing if LLM wraps in markdown
            clean_resp = response.replace("```json", "").replace("```", "").strip()
            data = json.loads(clean_resp)
        except Exception as e:
            import sys
            print(f"[ERROR] Failed to parse LLM response: {e}", file=sys.stderr)
            print(f"[DEBUG] Raw Response: {response}", file=sys.stderr)
            data = [] 
            
        snapshots = []
        for item in data:
            ds = DecisionSnapshot(
                case_study_id=case_id,
                source_pdf=source_id,
                inferred_time_window=item.get("inferred_time_window", "unknown"),
                location_context=item.get("location_context", ""),
                decision_context=item.get("decision_context", ""),
                uncertainties=item.get("uncertainties", []),
                risks_perceived=item.get("risks_perceived", []),
                actions_considered=item.get("actions_considered", []),
                action_taken_narrative=item.get("action_taken_narrative", "")
            )
            snapshots.append(ds)
            
        return snapshots
