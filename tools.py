import json
import os

def get_ticket_data(ticket_id=None):
    
    with open('tickets.json', 'r') as f:
        tickets = json.load(f)
    if ticket_id:
        return [t for t in tickets if t['ticket_id'].upper() == ticket_id.upper()]
    return tickets

def get_account_data(customer_name=None):
    
    with open('accounts.json', 'r') as f:
        accounts = json.load(f)
    if customer_name:
        return [a for a in accounts if a['customer_name'].lower() == customer_name.lower()]
    return accounts

def search_knowledge_base(query):
    
    docs = [
        'refund_policy.md', 'account_upgrade.md', 'api_rate_limits.md', 
        'security_practices.md', 'integration_setup.md'
    ]
    for doc in docs:
        if os.path.exists(doc):
            with open(doc, 'r') as f:
                content = f.read()
                # Simple keyword check to identify the correct document [cite: 66]
                if any(word.lower() in content.lower() for word in query.lower().split() if len(word) > 3):
                    return {"source": doc, "content": content}
    return None