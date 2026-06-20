"""
sutra_041: Knowledge Search
Pramana: Pratyaksha (Direct Perception)
Full-text search across Bharat Knowledge Archive
"""

import os
import json
import glob
import re
from difflib import SequenceMatcher

def execute(inputs: dict, context: dict = None) -> dict:
    query = inputs.get('query', '').lower()
    state = inputs.get('state', 'all')
    domain = inputs.get('domain', 'all')  # crops, medicinal_plants, etc.
    
    if not query:
        return {
            "status": "failure",
            "outputs": {},
            "trace": {
                "sutra_id": "sutra_041",
                "version": "1.0.0",
                "error": "Query required"
            }
        }
    
    # Load all data
    results = []
    data_dir = os.path.expanduser("~/soca/data")
    
    # Determine which states to search
    if state == 'all':
        state_dirs = [d for d in os.listdir(data_dir) if os.path.isdir(os.path.join(data_dir, d))]
    else:
        state_dirs = [state]
    
    for state_name in state_dirs:
        state_path = os.path.join(data_dir, state_name)
        if not os.path.exists(state_path):
            continue
        
        # Load JSON files
        json_files = glob.glob(os.path.join(state_path, "*.json"))
        for json_file in json_files:
            if domain != 'all' and domain not in json_file:
                continue
            
            try:
                with open(json_file, 'r') as f:
                    data = json.load(f)
                
                # Search within data
                for item in search_data(data, query):
                    item['state'] = state_name
                    item['source'] = os.path.basename(json_file)
                    results.append(item)
            except Exception as e:
                continue
    
    # Sort by relevance
    results = sorted(results, key=lambda x: x.get('score', 0), reverse=True)[:10]
    
    return {
        "status": "success",
        "outputs": {
            "query": query,
            "results": results,
            "count": len(results),
            "states_searched": state_dirs
        },
        "trace": {
            "sutra_id": "sutra_041",
            "version": "1.0.0"
        }
    }

def search_data(data, query):
    """Search within data structure."""
    results = []
    
    if isinstance(data, dict):
        for key in ['crops', 'plants', 'entries']:
            if key in data and isinstance(data[key], list):
                for item in data[key]:
                    score = score_item(item, query)
                    if score > 0.3:
                        results.append({
                            'data': item,
                            'score': score
                        })
    elif isinstance(data, list):
        for item in data:
            score = score_item(item, query)
            if score > 0.3:
                results.append({
                    'data': item,
                    'score': score
                })
    
    return results

def score_item(item, query):
    """Score an item based on query relevance."""
    if not isinstance(item, dict):
        return 0
    
    item_str = json.dumps(item).lower()
    
    if query in item_str:
        return 1.0
    
    query_words = query.split()
    matched = 0
    for word in query_words:
        if word in item_str:
            matched += 1
    
    if matched > 0:
        return matched / len(query_words) * 0.7
    
    return 0
