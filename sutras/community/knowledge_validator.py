"""
sutra_039: Knowledge Validator
Pramana: Pratyaksha (Direct Perception)
Validates community contributions
"""

import json
import sqlite3
import os
import re
from datetime import datetime

def execute(inputs: dict, context: dict = None) -> dict:
    contribution_id = inputs.get('contribution_id')
    action = inputs.get('action', 'validate')  # validate, reject, request_info
    validator = inputs.get('validator', 'system')
    
    if not contribution_id:
        return {
            "status": "failure",
            "outputs": {},
            "trace": {
                "sutra_id": "sutra_039",
                "version": "1.0.0",
                "error": "Contribution ID required"
            }
        }
    
    db_path = os.path.expanduser("~/soca/registry/community.db")
    
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        
        # Get contribution
        cursor.execute("""
            SELECT id, domain, data, contributor, location, status
            FROM contributions
            WHERE id = ?
        """, (contribution_id,))
        row = cursor.fetchone()
        
        if not row:
            return {
                "status": "failure",
                "outputs": {},
                "trace": {
                    "sutra_id": "sutra_039",
                    "version": "1.0.0",
                    "error": "Contribution not found"
                }
            }
        
        contrib_id, domain, data_str, contributor, location, status = row
        data = json.loads(data_str)
        
        # Validate based on domain
        validation_result = validate_knowledge(domain, data)
        
        if action == 'validate' and validation_result['valid']:
            new_status = 'approved'
            cursor.execute("""
                UPDATE contributions
                SET status = ?, validator = ?, validated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (new_status, validator, contribution_id))
            conn.commit()
            
            # Also add to knowledge graph
            add_to_knowledge_graph(domain, data, contributor, location)
            
            return {
                "status": "success",
                "outputs": {
                    "contribution_id": contribution_id,
                    "status": "approved",
                    "validated": True,
                    "reason": validation_result.get('reason', 'Valid knowledge')
                },
                "trace": {
                    "sutra_id": "sutra_039",
                    "version": "1.0.0"
                }
            }
        
        elif action == 'reject':
            cursor.execute("""
                UPDATE contributions
                SET status = 'rejected', validator = ?, validated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (validator, contribution_id))
            conn.commit()
            
            return {
                "status": "success",
                "outputs": {
                    "contribution_id": contribution_id,
                    "status": "rejected",
                    "validated": False
                },
                "trace": {
                    "sutra_id": "sutra_039",
                    "version": "1.0.0"
                }
            }
        
        else:
            return {
                "status": "failure",
                "outputs": {},
                "trace": {
                    "sutra_id": "sutra_039",
                    "version": "1.0.0",
                    "error": f"Validation failed: {validation_result.get('reason', 'Unknown')}"
                }
            }

def validate_knowledge(domain, data):
    """Validate knowledge based on domain rules."""
    if domain == 'agriculture':
        return validate_agriculture(data)
    elif domain == 'medicinal_plants':
        return validate_medicinal(data)
    elif domain == 'language':
        return validate_language(data)
    else:
        return {'valid': True, 'reason': 'General knowledge'}

def validate_agriculture(data):
    """Validate agriculture knowledge."""
    required_fields = ['crop', 'practice']
    for field in required_fields:
        if field not in data:
            return {'valid': False, 'reason': f'Missing field: {field}'}
    
    if len(str(data.get('practice', ''))) < 10:
        return {'valid': False, 'reason': 'Practice description too short'}
    
    return {'valid': True, 'reason': 'Valid agriculture knowledge'}

def validate_medicinal(data):
    """Validate medicinal plant knowledge."""
    required_fields = ['plant', 'uses']
    for field in required_fields:
        if field not in data:
            return {'valid': False, 'reason': f'Missing field: {field}'}
    
    if not data.get('uses') or len(data['uses']) < 1:
        return {'valid': False, 'reason': 'At least one use required'}
    
    return {'valid': True, 'reason': 'Valid medicinal knowledge'}

def validate_language(data):
    """Validate language knowledge."""
    required_fields = ['word', 'translation']
    for field in required_fields:
        if field not in data:
            return {'valid': False, 'reason': f'Missing field: {field}'}
    
    return {'valid': True, 'reason': 'Valid language knowledge'}

def add_to_knowledge_graph(domain, data, contributor, location):
    """Add validated knowledge to the knowledge graph."""
    # This will be implemented in v2.0
    pass
