"""
Register all Sutras from JSON files into the registry
"""

import sys
import os
import json
import glob

# Add runtime to path
sys.path.append('runtime')
from registry_manager import RegistryManager

def register_all_sutras():
    registry = RegistryManager()
    
    sutra_dir = "sutras"
    json_files = glob.glob(os.path.join(sutra_dir, "*.json"))
    
    print(f"Found {len(json_files)} JSON files in {sutra_dir}")
    
    registered = 0
    for json_file in json_files:
        try:
            with open(json_file, 'r') as f:
                sutra_json = json.load(f)
            registry.register_sutra(sutra_json)
            print(f"✅ Registered: {sutra_json.get('sutra_id')} - {sutra_json.get('name')}")
            registered += 1
        except Exception as e:
            print(f"❌ Failed to register {json_file}: {e}")
    
    stats = registry.get_stats()
    print(f"\nRegistry Stats:")
    print(f"  Total Sutras: {stats['total_sutras']}")
    print(f"  Total Traces: {stats['total_traces']}")
    print(f"  Total Usage: {stats['total_usage']}")
    
    print(f"\n✅ Registered {registered} sutras successfully")

if __name__ == "__main__":
    register_all_sutras()
