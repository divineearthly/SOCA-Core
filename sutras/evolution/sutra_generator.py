"""
Sutra 016: Sutra Generator
Generates new Sutras based on discovered gaps
"""

import json
import os
import hashlib
from datetime import datetime

def execute(inputs: dict, context: dict = None) -> dict:
    """
    Generate a new Sutra based on a gap.
    
    Args:
        inputs: dict with:
            - gap: gap description
            - sutra_id: optional specific ID
            - template: template to use
    
    Returns:
        dict with generated sutra
    """
    gap = inputs.get('gap', {})
    sutra_id = inputs.get('sutra_id', None)
    template = inputs.get('template', 'basic')
    
    # Generate sutra based on gap type
    gap_type = gap.get('type', 'unknown')
    
    if gap_type == 'missing_category':
        category = gap.get('category', 'general')
        sutra = generate_category_sutra(category, sutra_id)
    else:
        sutra = generate_generic_sutra(gap, sutra_id)
    
    return {
        "status": "success",
        "outputs": {
            "sutra": sutra,
            "gap": gap
        },
        "trace": {
            "sutra_id": "sutra_016",
            "version": "1.0.0",
            "generated": sutra.get('name', 'unknown')
        }
    }

def generate_category_sutra(category, sutra_id):
    """Generate a sutra for a missing category."""
    templates = {
        'arithmetic': {
            'name': f'Generic {category.title()} Operation',
            'type': category,
            'category': 'core',
            'pramana': 'pratyaksha',
            'inputs': [{"name": "a", "type": "float", "required": True}],
            'outputs': [{"name": "result", "type": "float"}],
            'description': f'Performs {category} operations'
        },
        'planning': {
            'name': f'Generic {category.title()} Planner',
            'type': category,
            'category': 'core',
            'pramana': 'anumana',
            'inputs': [{"name": "tasks", "type": "array", "required": True}],
            'outputs': [{"name": "plan", "type": "array"}],
            'description': f'Creates {category} plans'
        }
    }
    
    template = templates.get(category, templates.get('general', {}))
    
    if not sutra_id:
        sutra_id = f"sutra_{get_next_id()}"
    
    return {
        "schema_version": "0.1.0",
        "sutra_id": sutra_id,
        "sutra_version": "1.0.0",
        "compatibility": ["0.1.x"],
        **template
    }

def get_next_id():
    """Get the next available sutra ID."""
    import glob
    import re
    
    sutra_dir = os.path.expanduser("~/soca/sutras")
    json_files = glob.glob(os.path.join(sutra_dir, "sutra_*.json"))
    
    max_id = 0
    for f in json_files:
        match = re.search(r'sutra_(\d+)', f)
        if match:
            max_id = max(max_id, int(match.group(1)))
    
    return max_id + 1

def generate_generic_sutra(gap, sutra_id):
    """Generate a generic sutra."""
    return {
        "schema_version": "0.1.0",
        "sutra_id": sutra_id or f"sutra_{get_next_id()}",
        "sutra_version": "1.0.0",
        "compatibility": ["0.1.x"],
        "name": f"Sutra for {gap.get('suggestion', 'unknown')[:30]}",
        "type": "general",
        "category": "core",
        "pramana": "anumana",
        "inputs": [],
        "outputs": [],
        "prerequisites": [],
        "operation": {
            "module": "sutras.general.generic",
            "entry_point": "execute"
        },
        "validation": {"tests": []}
    }
