from tools import get_ticket_data, get_account_data

def get_priority_triage():
    """Ranks open tickets based on priority, tier, and account health [cite: 99-105]."""
    tickets = get_ticket_data()
    accounts = {a['customer_name']: a for a in get_account_data()}
    
    scored_list = []
    for t in tickets:
        if t['status'] != 'open': 
            continue
        
        score = 0
        reasons = []
        
        # Criteria logic
        if t['priority'] == 'urgent':
            score += 50
            reasons.append("Urgent priority ticket")
        if t['customer_tier'] == 'enterprise':
            score += 30
            reasons.append("Enterprise tier customer")
            
        acc = accounts.get(t['customer_name'], {})
        health = acc.get('health_score', 100)
        if health < 50:
            score += 20
            reasons.append(f"Low account health score ({health})")
            
        scored_list.append({
            "ticket_id": t['ticket_id'],
            "customer": t['customer_name'],
            "score": score,
            "reasoning": ". ".join(reasons)
        })
    
    # Sort by score descending 
    return sorted(scored_list, key=lambda x: x['score'], reverse=True)[:3]