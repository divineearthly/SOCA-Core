"""
Memory Integration for Multi-Sutra Planner
Uses Kosha-Net Memory (sutra_013)
"""

import sys
sys.path.append('runtime')
from soca_runtime import SOCARuntime

class MemoryIntegration:
    def __init__(self):
        self.runtime = SOCARuntime()
        self.session_memory = {}
    
    def store_context(self, key: str, value: any):
        """Store context in session memory."""
        self.session_memory[key] = value
        
        # Also try to store in Kosha-Net Memory
        try:
            result = self.runtime.solve_sequence(
                ["sutra_013"],
                {
                    "action": "store",
                    "key": f"context_{key}",
                    "value": value,
                    "layer": "manomaya",
                    "ttl": 3600
                }
            )
        except:
            pass
    
    def get_context(self, key: str) -> any:
        """Get context from session memory."""
        if key in self.session_memory:
            return self.session_memory[key]
        
        # Try to retrieve from Kosha-Net Memory
        try:
            result = self.runtime.solve_sequence(
                ["sutra_013"],
                {
                    "action": "retrieve",
                    "key": f"context_{key}"
                }
            )
            if result.get('status') == 'success' and result.get('outputs', {}).get('found'):
                value = result['outputs'].get('value')
                self.session_memory[key] = value
                return value
        except:
            pass
        
        return None
    
    def get_all_context(self) -> dict:
        """Get all stored context."""
        return self.session_memory.copy()
    
    def clear_context(self):
        """Clear session memory."""
        self.session_memory = {}
