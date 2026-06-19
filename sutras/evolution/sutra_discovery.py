"""
Sutra 015: Sutra Discovery
Identifies gaps in system capabilities
"""

import json
import sqlite3
import os
import hashlib
from datetime import datetime

def execute(inputs: dict, context: dict = None) -> dict:
    """
    Discover gaps in system capabilities.
    
    Args:
        inputs: dict with:
            - target_domain: domain to analyze
            - max_gaps: max number of gaps to find
    
    Returns:
        dict with discovered gaps
    """
    target_domain = inputs.get('target_domain', 'all')
    max_gaps = inputs.get('max_gaps', 5)
    
    # Get current sutras
    sutras = get_existing_sutras()
    
    # Analyze capabilities
    gaps = analyze_gaps(sutras, target_domain, max_gaps)
    
    return {
        "status": "success",
        "outputs": {
            "total_sutras": len(sutras),
            "gaps": gaps,
            "gap_count": len(gaps)
        },
        "trace": {
            "sutra_id": "sutra_015",
            "version": "1.0.0",
            "target_domain": target_domain
        }
    }

def get_existing_sutras():
    """Get all registered sutras from database."""
    db_path = os.path.expanduser("~/soca/registry/soca.db")
    
    if not os.path.exists(db_path):
        return []
    
    try:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT sutra_id, name, category, pramana
                FROM sutra_registry
                WHERE is_active = TRUE
            """)
            return cursor.fetchall()
    except:
        return []

def analyze_gaps(sutras, domain, max_gaps):
    """Analyze capability gaps."""
    gaps = []
    
    # Define expected categories
    expected_categories = [
        'arithmetic',
        'logic',
        'planning',
        'meta',
        'codegen',
        'llm',
        'memory',
        'learning',
        'evolution'
    ]
    
    # Check which categories are missing
    existing_categories = set([s[2] for s in sutras if len(s) > 2])
    
    for category in expected_categories:
        if category not in existing_categories:
            gaps.append({
                'type': 'missing_category',
                'category': category,
                'suggestion': f'Create sutra for {category} operations'
            })
            if len(gaps) >= max_gaps:
                break
    
    # If no gaps found, suggest improvements
    if not gaps:
        gaps.append({
            'type': 'optimization',
            'suggestion': 'Consider creating specialized Sutras for frequently used patterns'
        })
    
    return gaps[:max_gaps]
