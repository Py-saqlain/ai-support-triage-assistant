import os
import json
from groq import Groq
from dotenv import load_dotenv
from tools import get_ticket_data, get_account_data, search_knowledge_base
from triage import get_priority_triage

load_dotenv()
test_key = os.getenv("GROQ_API_KEY")
print(f"DEBUG: Loaded Key is: {test_key}")
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def get_llm_decision(query):
    """Determines the route and logic for the query."""
    system_prompt = """
    You are a triage router. Analyze the query and return a JSON object with:
    'route': KNOWLEDGE_BASE, TICKET_LOOKUP, ACCOUNT_LOOKUP, AMBIGUOUS, or UNSUPPORTED.
    'confidence': float 0-1.
    'extracted_id': Any Ticket ID (like T-2001) or Customer Name mentioned, else null.
    """
    
    response = client.chat.completions.create(
        messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": query}],
        model="llama-3.1-8b-instant",  # Use this updated model name
        response_format={"type": "json_object"}
    )
    return json.loads(response.choices[0].message.content)

def run_assistant(query):
    decision = get_llm_decision(query)
    route = decision['route']
    output = {
        "route": route,
        "confidence": decision['confidence'],
        "used_sources": [],
        "used_tools": [],
        "needs_clarification": False,
        "final_answer": ""
    }

    # Routing logic
    if "handle first" in query.lower() or "triage" in query.lower():
        triage_results = get_priority_triage()
        output["used_sources"] = ["tickets.json", "accounts.json"]
        output["final_answer"] = f"Priority Triage: {triage_results}"
        
    elif route == "TICKET_LOOKUP":
        data = get_ticket_data(decision.get('extracted_id'))
        output["used_sources"] = ["tickets.json"]
        output["final_answer"] = str(data) if data else "Ticket not found."
        
    elif route == "KNOWLEDGE_BASE":
        kb = search_knowledge_base(query)
        if kb:
            output["used_sources"] = [kb['source']]
            output["final_answer"] = kb['content']
        else:
            output["route"] = "UNSUPPORTED"
            output["final_answer"] = "I cannot find this in our policy documents." 
            
    elif route == "AMBIGUOUS":
        output["needs_clarification"] = True
        output["final_answer"] = "Could you please provide a specific ticket ID or customer name?"
        
    elif route == "UNSUPPORTED":
        output["final_answer"] = "I'm sorry, I don't have information regarding that request." 

    return output

if __name__ == "__main__":
    user_query = input("How can I help you? Please add your request!")
    print(json.dumps(run_assistant(user_query), indent=2))