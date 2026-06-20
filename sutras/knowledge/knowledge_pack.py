"""
sutra_058: Village Knowledge Pack
Pramana: Pratyaksha (Direct Perception)
Creates and installs offline knowledge packs
"""

import os
import json
import shutil
from datetime import datetime

def execute(inputs: dict, context: dict = None) -> dict:
    action = inputs.get('action', 'create')
    pack_name = inputs.get('pack_name', '')
    pack_data = inputs.get('pack_data', {})
    install_path = inputs.get('install_path', '~/soca/data/packs')
    
    install_path = os.path.expanduser(install_path)
    os.makedirs(install_path, exist_ok=True)
    
    if action == 'create':
        if not pack_name or not pack_data:
            return {
                "status": "failure",
                "outputs": {},
                "trace": {
                    "sutra_id": "sutra_058",
                    "version": "1.0.0",
                    "error": "Pack name and data required"
                }
            }
        
        pack_file = os.path.join(install_path, f"{pack_name}.pack")
        with open(pack_file, 'w') as f:
            json.dump({
                'name': pack_name,
                'created': datetime.now().isoformat(),
                'data': pack_data
            }, f, indent=2)
        
        return {
            "status": "success",
            "outputs": {
                "action": "create",
                "pack_name": pack_name,
                "file": pack_file,
                "size": os.path.getsize(pack_file)
            },
            "trace": {
                "sutra_id": "sutra_058",
                "version": "1.0.0"
            }
        }
    
    elif action == 'install':
        pack_file = os.path.join(install_path, f"{pack_name}.pack")
        if not os.path.exists(pack_file):
            return {
                "status": "failure",
                "outputs": {},
                "trace": {
                    "sutra_id": "sutra_058",
                    "version": "1.0.0",
                    "error": f"Pack '{pack_name}' not found"
                }
            }
        
        with open(pack_file, 'r') as f:
            pack = json.load(f)
        
        return {
            "status": "success",
            "outputs": {
                "action": "install",
                "pack_name": pack_name,
                "data": pack.get('data', {})
            },
            "trace": {
                "sutra_id": "sutra_058",
                "version": "1.0.0"
            }
        }
    
    elif action == 'list':
        packs = []
        for f in os.listdir(install_path):
            if f.endswith('.pack'):
                packs.append(f.replace('.pack', ''))
        return {
            "status": "success",
            "outputs": {
                "packs": packs
            },
            "trace": {
                "sutra_id": "sutra_058",
                "version": "1.0.0"
            }
        }
    
    return {
        "status": "failure",
        "outputs": {},
        "trace": {
            "sutra_id": "sutra_058",
            "version": "1.0.0",
            "error": f"Unknown action: {action}"
        }
    }
