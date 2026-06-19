"""
SOCA Runtime: Sutra-Oriented Cognitive Architecture
DAG-based execution engine with provenance tracking
"""

import networkx as nx
import importlib
import json
import time
import uuid
import os
from typing import List, Dict, Any

# Use relative import
from .registry_manager import RegistryManager

class SOCARuntime:
    def __init__(self, registry_path: str = "registry/soca.db"):
        self.registry = RegistryManager(registry_path)
        self.graph = nx.DiGraph()
        self.trace = []
        self.results = {}
    
    def load_sutra(self, sutra_id: str):
        """Load a Sutra's executable function."""
        sutra_def = self.registry.get_sutra(sutra_id)
        if not sutra_def:
            raise ValueError(f"Sutra {sutra_id} not found in registry")
        
        try:
            module = importlib.import_module(sutra_def['module_path'])
            func = getattr(module, sutra_def['entry_point'])
            return func
        except ImportError as e:
            raise ImportError(f"Could not import {sutra_def['module_path']}: {e}")
        except AttributeError as e:
            raise AttributeError(f"Could not find {sutra_def['entry_point']} in {sutra_def['module_path']}: {e}")
    
    def build_graph_from_list(self, sutra_ids: List[str]):
        """Build a graph from a list of sutra IDs in execution order."""
        for sutra_id in sutra_ids:
            sutra_def = self.registry.get_sutra(sutra_id)
            if sutra_def:
                self.graph.add_node(sutra_id, definition=sutra_def)
        
        for i in range(len(sutra_ids) - 1):
            self.graph.add_edge(sutra_ids[i], sutra_ids[i+1])
    
    def execute_graph(self, inputs: Dict, sutra_order: List[str] = None) -> Dict:
        """Execute the DAG in topological order."""
        results = {}
        traces = []
        start_time = time.time()
        
        if sutra_order is None:
            try:
                order = list(nx.topological_sort(self.graph))
            except nx.NetworkXUnfeasible:
                return {
                    "status": "failure",
                    "error": "Graph contains a cycle",
                    "trace": {"executed_sutras": []}
                }
        else:
            order = sutra_order
        
        for sutra_id in order:
            try:
                sutra_func = self.load_sutra(sutra_id)
            except Exception as e:
                return {
                    "status": "failure",
                    "error": f"Failed to load sutra {sutra_id}: {str(e)}",
                    "trace": {"executed_sutras": traces}
                }
            
            sutra_inputs = {}
            sutra_def = self.registry.get_sutra(sutra_id)
            if sutra_def:
                sutra_inputs = {**inputs, **results}
            
            try:
                exec_result = sutra_func(sutra_inputs)
                
                if exec_result['status'] == 'success':
                    if 'outputs' in exec_result:
                        for key, value in exec_result['outputs'].items():
                            results[key] = value
                    
                    self.registry.record_usage(sutra_id, True)
                    
                    trace_entry = {
                        "id": sutra_id,
                        "version": exec_result.get('trace', {}).get('sutra_version', 'unknown'),
                        "status": "success",
                        "execution_time_ms": exec_result.get('trace', {}).get('execution_time_ms', 0)
                    }
                    traces.append(trace_entry)
                else:
                    self.registry.record_usage(sutra_id, False)
                    return {
                        "status": "failure",
                        "error": f"Sutra {sutra_id} failed: {exec_result.get('trace', {}).get('error', 'Unknown error')}",
                        "trace": {"executed_sutras": traces + [{"id": sutra_id, "status": "failure"}]}
                    }
            except Exception as e:
                self.registry.record_usage(sutra_id, False)
                return {
                    "status": "failure",
                    "error": f"Sutra {sutra_id} raised exception: {str(e)}",
                    "trace": {"executed_sutras": traces + [{"id": sutra_id, "status": "failure"}]}
                }
        
        trace_id = str(uuid.uuid4())[:8]
        trace_data = {
            "trace_id": trace_id,
            "executed_sutras": traces,
            "status": "success",
            "total_execution_time_ms": int((time.time() - start_time) * 1000),
            "results": results
        }
        
        self.registry.log_trace(trace_data)
        
        return {
            "status": "success",
            "outputs": results,
            "trace": trace_data
        }
    
    def solve_sequence(self, sutra_ids: List[str], inputs: Dict) -> Dict:
        """Solve a problem by executing a sequence of Sutras."""
        self.graph = nx.DiGraph()
        self.results = {}
        self.build_graph_from_list(sutra_ids)
        return self.execute_graph(inputs, sutra_ids)
    
    def register_sutras_from_directory(self, sutra_dir: str = "sutras"):
        """Register all Sutras from JSON files in a directory."""
        import glob
        
        if not os.path.exists(sutra_dir):
            print(f"Directory {sutra_dir} not found")
            return
        
        json_files = glob.glob(os.path.join(sutra_dir, "*.json"))
        for json_file in json_files:
            try:
                with open(json_file, 'r') as f:
                    sutra_json = json.load(f)
                self.registry.register_sutra(sutra_json)
                print(f"Registered: {sutra_json.get('sutra_id', 'unknown')}")
            except Exception as e:
                print(f"Failed to register {json_file}: {e}")
    
    def get_stats(self) -> dict:
        """Get runtime statistics."""
        return self.registry.get_stats()
