"""
sutra_095: Confidence Calibrator
Pramana: Anumana (Inference)
Calibrates confidence based on historical accuracy
"""

import sys
import sqlite3
import os
sys.path.append('runtime')
from response import success_response, failure_response

def execute(inputs: dict, context: dict = None) -> dict:
    predicted = inputs.get('predicted_confidence', 0.5)
    intent = inputs.get('intent', 'general')
    
    db_path = os.path.expanduser("~/soca/registry/soca.db")
    
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        
        # Get historical accuracy for this intent
        cursor.execute("""
            SELECT AVG(confidence) 
            FROM telemetry 
            WHERE intent = ? AND confidence > 0
        """, (intent,))
        row = cursor.fetchone()
        historical_avg = row[0] if row[0] else 0.5
        
        # Calibrate
        calibrated = (predicted + historical_avg) / 2
        
        return success_response(
            outputs={
                'predicted': round(predicted, 3),
                'historical_avg': round(historical_avg, 3),
                'calibrated': round(calibrated, 3),
                'intent': intent
            },
            confidence=calibrated
        )
