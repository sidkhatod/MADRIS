from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
load_dotenv()

import sys
import os
# Add the parent directory (backend) to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.llm_service import create_llm_client
from services.ingest_service import IngestService
from services.memory_service import MemoryService
from services.reasoning_service import ReasoningService

app = Flask(__name__)
CORS(app) # Enable CORS for all routes

# Initialize Services via Factory
try:
    llm_client = create_llm_client()
    print("LLM Client initialized successfully.")
except Exception as e:
    print(f"CRITICAL: Failed to initialize LLM Client: {e}")
    # strict backend requirement: fail fast
    import sys
    sys.exit(1) 

@app.route('/', methods=['GET'])
@app.route('/api/', methods=['GET'])
def index():
    return jsonify({
        "status": "ok",
        "service": "Antigravity Decision Support Backend",
        "endpoints": [
            "/api/ingest/case-study [POST]",
            "/api/reasoning/decision-support [POST]",
            "/api/memory/retrieve [POST]"
        ]
    })

ingest_service = IngestService(llm_client)
memory_service = MemoryService()
reasoning_service = ReasoningService(llm_client)

@app.route('/api/ingest/case-study', methods=['POST'])
def ingest_case_study():
    """
    Ingests raw text, generates snapshots, embeds, and stores them.
    Input: { "case_study_id": "...", "raw_text": "..." }
    """
    data = request.json
    case_text = data.get('raw_text') or data.get('text') # Support both for robustness
    case_id = data.get('case_study_id') or data.get('case_id')
    # Frontend doesn't strictly send source_id yet, default to 'manual_input'
    source_id = data.get('source_id', 'manual_input')
    
    if not case_text or not case_id:
        return jsonify({"status": "error", "message": "Missing required fields: raw_text, case_study_id"}), 400

    # 1. Generate Snapshots
    snapshots = ingest_service.processed_case_study(case_text, source_id, case_id)
    
    # 2. Embed
    embeddings = [llm_client.embed_text(snap.narrative_text) for snap in snapshots]
    
    # 3. Store
    memory_service.store_snapshots(snapshots, embeddings)
    
    return jsonify({
        "status": "success",
        "snapshots_created": len(snapshots)
    })

@app.route('/api/reasoning/decision-support', methods=['POST'])
def reasoning_support():
    """
    Main endgame endpoint: User sends current narrative -> System retrieves & reasons.
    Input: { "current_narrative": "..." }
    """
    data = request.json
    current_narrative = data.get('current_narrative') or data.get('narrative')
    
    if not current_narrative:
        return jsonify({"status": "error", "message": "Missing current_narrative"}), 400

    # 1. Embed current narrative
    query_vector = llm_client.embed_text(current_narrative)
    
    # 2. Retrieve similar decision snapshots
    # Returns List[Tuple[DecisionSnapshot, float]]
    retrieved_results = memory_service.retrieve_relevant(query_vector, limit=5)
    
    # Extract snapshots for reasoning service
    relevant_snapshots = [r[0] for r in retrieved_results]
    
    # 3. LLM Reasoning (Get Narrative Explanation)
    # The Reasoning Service returns a Dict with 'analysis' (text) and 'driving_snapshots' (ids)
    reasoning_output = reasoning_service.generate_decision_support(current_narrative, relevant_snapshots)
    explanation_text = reasoning_output.get("analysis", "")
    
    # 4. Construct Structured Response (Aggregation Logic)
    # We aggregate risks and actions from the *retrieved snapshots* themselves to form the structured lists
    aggregated_risks = []
    aggregated_actions = []
    historical_basis = []
    
    seen_risks = set()
    seen_actions = set()

    for snap, score in retrieved_results:
        # Format Historical Basis
        historical_basis.append({
            "case_study_id": snap.case_study_id,
            "inferred_time_window": snap.inferred_time_window,
            "excerpt": snap.decision_context,
            "similarity_score": score
        })
        
        # Aggregate Risks
        for risk in snap.risks_perceived:
            clean_risk = risk.strip()
            if clean_risk and clean_risk.lower() not in seen_risks:
                aggregated_risks.append(clean_risk)
                seen_risks.add(clean_risk.lower())
        
        # Aggregate Actions (using action_taken_narrative or actions_considered)
        # Assuming action_taken_narrative is a string, we might treat it as a single item or try to split if it looks like a list
        # For now, treat the main narrative action as the recommended action item
        action_text = snap.action_taken_narrative.strip()
        if action_text and action_text.lower() not in seen_actions:
             aggregated_actions.append(action_text)
             seen_actions.add(action_text.lower())
    
    # Fallback if no risks/actions found
    if not aggregated_risks:
        aggregated_risks = ["Risk assessment requires more data."]
    if not aggregated_actions:
        aggregated_actions = ["Evaluate situation further."]

    return jsonify({
        "top_risks": aggregated_risks[:5], # Limit to top 5
        "recommended_actions": aggregated_actions[:5], # Limit to top 5
        "explanation": explanation_text,
        "historical_basis": historical_basis
    })

@app.route('/api/memory/retrieve', methods=['POST'])
def debug_retrieve():
    """
    Retrieve endpoint for Past Disasters page.
    Input: { "query_text": "...", "top_k": 5 }
    """
    data = request.json
    query_text = data.get('query_text') or data.get('query')
    top_k = data.get('top_k', 5)
    
    if not query_text:
        return jsonify([])

    query_vector = llm_client.embed_text(query_text)
    # Returns List[Tuple[DecisionSnapshot, float]]
    results = memory_service.retrieve_relevant(query_vector, limit=top_k)
    
    response_list = []
    for snap, score in results:
        item = snap.to_dict()
        item["similarity_score"] = score
        response_list.append(item)
        
    return jsonify(response_list)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
