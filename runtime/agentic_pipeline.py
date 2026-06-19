"""
SOCA Agentic Pipeline v9.0 - Iterative Planner + Slot Filling
"""

import sys
import time
import re
import json
import os
sys.path.append('runtime')
from soca_runtime import SOCARuntime

class AgenticPipeline:
    def __init__(self):
        self.runtime = SOCARuntime()
        self.trace = []
        self.max_iterations = 3
    
    def process(self, query: str, user_id: str = "anonymous") -> dict:
        start_time = time.time()
        self.trace = []
        
        # Initialize working memory with slot tracking
        working_memory = {
            "query": query,
            "user_id": user_id,
            "language": "en",
            "intent": None,
            "profile": {},
            "context": {},
            "knowledge": [],
            "ranked_knowledge": [],
            "evidence": [],
            "results": {},
            "synthesis": "",
            "confidence": 0.5,
            "approved": False,
            "sources": [],
            "trace": [],
            "pending_slots": {
                "season": None,
                "soil_type": None,
                "district": None
            },
            "iteration": 0,
            "goal_reached": False
        }
        
        # Fill initial slots from query
        self._fill_slots_from_query(query, working_memory)
        
        # Load profile and fill slots
        self._load_profile(user_id, working_memory)
        
        # Main planning loop
        for iteration in range(self.max_iterations):
            working_memory["iteration"] = iteration + 1
            
            # Check if all required slots are filled
            if self._all_slots_filled(working_memory):
                working_memory["goal_reached"] = True
                break
            
            # If this is the first iteration, ask for missing slots
            if iteration == 0 and not self._all_slots_filled(working_memory):
                missing = self._get_missing_slots(working_memory)
                return {
                    "status": "needs_clarification",
                    "questions": self._generate_questions(missing),
                    "missing_slots": missing,
                    "query": query,
                    "intent": working_memory["intent"],
                    "trace": self.trace,
                    "elapsed_ms": round((time.time() - start_time) * 1000, 1)
                }
            
            # Execute reasoning
            result = self._execute_reasoning(working_memory)
            if result:
                return result
        
        # Final reasoning after slots are filled
        if working_memory["goal_reached"]:
            return self._execute_full_reasoning(working_memory, start_time)
        
        return {
            "status": "failure",
            "error": "Max iterations reached without resolution",
            "query": query,
            "elapsed_ms": round((time.time() - start_time) * 1000, 1)
        }
    
    def _fill_slots_from_query(self, query: str, working_memory: dict):
        """Extract and fill slots from query."""
        query_lower = query.lower()
        
        # District
        districts = ["bongaigaon", "barpeta", "jorhat", "nagaon", "dibrugarh",
                    "sonitpur", "dhubri", "goalpara", "kokrajhar", "tinsukia",
                    "sivasagar", "golaghat", "lakhimpur", "dhemaji", "morigaon",
                    "nalbari", "kamrup", "cachar", "hailakandi", "karimganj"]
        for district in districts:
            if district in query_lower:
                working_memory["pending_slots"]["district"] = district
                working_memory["context"]["district"] = district
                break
        if "assam" in query_lower and not working_memory["pending_slots"]["district"]:
            working_memory["pending_slots"]["district"] = "assam"
        
        # Season
        seasons = ["kharif", "rabi", "summer", "winter"]
        for season in seasons:
            if season in query_lower:
                working_memory["pending_slots"]["season"] = season
                working_memory["context"]["season"] = season
                break
    
    def _load_profile(self, user_id: str, working_memory: dict):
        """Load profile and fill slots."""
        profile_result = self._execute("sutra_076", {
            "action": "load",
            "user_id": user_id
        })
        if profile_result.get("status") == "success":
            profile = profile_result.get("outputs", {}).get("profile", {})
            working_memory["profile"] = profile
            
            # Fill slots from profile if not already set
            if profile.get("district") and not working_memory["pending_slots"]["district"]:
                working_memory["pending_slots"]["district"] = profile["district"]
                working_memory["context"]["district"] = profile["district"]
            
            if profile.get("soil_type") and not working_memory["pending_slots"]["soil_type"]:
                working_memory["pending_slots"]["soil_type"] = profile["soil_type"]
    
    def _all_slots_filled(self, working_memory: dict) -> bool:
        """Check if all required slots are filled."""
        required = ["season"]
        # Only require district if not agriculture
        if working_memory.get("intent") == "agriculture":
            required.append("district")
        
        for slot in required:
            if not working_memory["pending_slots"].get(slot):
                return False
        return True
    
    def _get_missing_slots(self, working_memory: dict) -> list:
        """Get list of missing slots."""
        missing = []
        if not working_memory["pending_slots"].get("district"):
            missing.append("district")
        if not working_memory["pending_slots"].get("season"):
            missing.append("season")
        if not working_memory["pending_slots"].get("soil_type"):
            missing.append("soil_type")
        return missing
    
    def _generate_questions(self, missing: list) -> list:
        """Generate questions for missing slots."""
        questions = []
        for slot in missing:
            if slot == "district":
                questions.append("Which district are you in?")
            elif slot == "season":
                questions.append("Which season are you planning to grow in? (kharif/rabi/summer)")
            elif slot == "soil_type":
                questions.append("What type of soil do you have? (loamy/clay/sandy)")
        return questions
    
    def _execute_reasoning(self, working_memory: dict) -> dict:
        """Execute reasoning with current slots."""
        # This would be the full reasoning pipeline
        # For now, return None to continue loop
        return None
    
    def _execute_full_reasoning(self, working_memory: dict, start_time: float) -> dict:
        """Execute full reasoning after all slots are filled."""
        # Intent Classification
        intent_result = self._execute("sutra_045", {"query": working_memory["query"]})
        if intent_result.get("status") == "success":
            working_memory["intent"] = intent_result.get("outputs", {}).get("intent", "general")
        self._add_trace("intent", working_memory["intent"])
        
        # Knowledge Retrieval
        knowledge_result = self._execute("sutra_074", {
            "query": working_memory["query"],
            "district": working_memory["pending_slots"].get("district", ""),
            "crop": ""
        })
        if knowledge_result.get("status") == "success":
            working_memory["knowledge"] = knowledge_result.get("outputs", {}).get("knowledge_results", [])
        self._add_trace("knowledge", len(working_memory["knowledge"]))
        
        # BM25 Ranking (sutra_080)
        ranker_result = self._execute("sutra_080", {
            "query": working_memory["query"],
            "knowledge_results": working_memory["knowledge"],
            "top_k": 5
        })
        if ranker_result.get("status") == "success":
            working_memory["ranked_knowledge"] = ranker_result.get("outputs", {}).get("ranked_results", [])
        self._add_trace("bm25", len(working_memory["ranked_knowledge"]))
        
        # Query Planner
        planner_result = self._execute("sutra_069", {
            "query": working_memory["query"],
            "intent": working_memory["intent"]
        })
        sequence = planner_result.get("outputs", {}).get("sequence", ["sutra_041"])
        
        # Domain Sutras
        results = {}
        for sutra_id in sequence:
            if sutra_id in ["sutra_068", "sutra_069", "sutra_070", "sutra_071", "sutra_072",
                           "sutra_073", "sutra_074", "sutra_075", "sutra_076", "sutra_077",
                           "sutra_078", "sutra_079", "sutra_080"]:
                continue
            
            inputs = {
                "query": working_memory["query"],
                "location": working_memory["pending_slots"].get("district", ""),
                "district": working_memory["pending_slots"].get("district", ""),
                "season": working_memory["pending_slots"].get("season", ""),
                "soil_type": working_memory["pending_slots"].get("soil_type", ""),
                "crop_history": working_memory["profile"].get("crop_history", [])
            }
            
            result = self._execute(sutra_id, inputs)
            if result.get("status") == "success":
                outputs = result.get("outputs", {})
                results[sutra_id] = outputs
                for k, v in outputs.items():
                    if v not in [None, "", []]:
                        if k not in working_memory["results"]:
                            working_memory["results"][k] = []
                        if isinstance(v, list):
                            for item in v:
                                if item not in working_memory["results"][k]:
                                    working_memory["results"][k].append(item)
                        else:
                            if v not in working_memory["results"][k]:
                                working_memory["results"][k].append(v)
        
        self._add_trace("domain", len(results))
        
        # Multi-Hop Reasoner
        reasoner_result = self._execute("sutra_070", {
            "results": results,
            "query": working_memory["query"],
            "context": working_memory["context"],
            "ranked_knowledge": working_memory["ranked_knowledge"]
        })
        if reasoner_result.get("status") == "success":
            working_memory["synthesis"] = reasoner_result.get("outputs", {}).get("synthesis", "")
            working_memory["sources"] = reasoner_result.get("outputs", {}).get("sources", [])
        self._add_trace("reasoner", working_memory["synthesis"][:50])
        
        # Evidence Quality Scorer
        quality_result = self._execute("sutra_079", {
            "answer": working_memory["synthesis"],
            "sources": working_memory["sources"],
            "ranked_results": working_memory["ranked_knowledge"],
            "domain": working_memory["intent"]
        })
        if quality_result.get("status") == "success":
            working_memory["confidence"] = quality_result.get("outputs", {}).get("quality_score", 0.5)
        
        # Response Validator
        validator_result = self._execute("sutra_072", {
            "response": working_memory["synthesis"],
            "confidence": working_memory["confidence"],
            "sources": working_memory["sources"]
        })
        if validator_result.get("status") == "success":
            working_memory["approved"] = validator_result.get("outputs", {}).get("approved", False)
        
        elapsed = time.time() - start_time
        
        return {
            "status": "success",
            "query": working_memory["query"],
            "intent": working_memory["intent"],
            "answer": working_memory["synthesis"],
            "confidence": working_memory["confidence"],
            "approved": working_memory["approved"],
            "sources": working_memory["sources"],
            "profile": working_memory["profile"],
            "context": working_memory["context"],
            "slots_filled": working_memory["pending_slots"],
            "ranked_knowledge": working_memory["ranked_knowledge"][:3],
            "trace": self.trace,
            "iteration": working_memory["iteration"],
            "elapsed_ms": round(elapsed * 1000, 1)
        }
    
    def _execute(self, sutra_id: str, inputs: dict) -> dict:
        try:
            result = self.runtime.solve_sequence([sutra_id], inputs)
            return result
        except Exception as e:
            return {
                "status": "failure",
                "outputs": {"error": str(e)},
                "confidence": 0.0
            }
    
    def _add_trace(self, step: str, value):
        if isinstance(value, list):
            value = str(value[:3]) if len(value) > 3 else str(value)
        self.trace.append({"step": step, "value": str(value)[:50]})
    
    def explain(self, query: str) -> str:
        result = self.process(query)
        
        if result.get("status") == "needs_clarification":
            lines = ["=" * 50, f"📝 Query: {query}", "=" * 50, "❓ Clarification Needed:"]
            for q in result.get("questions", []):
                lines.append(f"  ├── {q}")
            lines.append("=" * 50)
            return "\n".join(lines)
        
        lines = [
            "=" * 50,
            f"📝 Query: {query}",
            "=" * 50,
            f"🎯 Intent: {result['intent']}",
            f"📊 Confidence: {result['confidence']:.2f}",
            f"✅ Approved: {result['approved']}",
            f"🔄 Iteration: {result.get('iteration', 1)}",
            f"⏱️ Time: {result['elapsed_ms']:.1f}ms",
            "",
            "📋 Slots Filled:"
        ]
        for k, v in result.get('slots_filled', {}).items():
            if v:
                lines.append(f"  ├── {k}: {v}")
        
        lines.append("")
        lines.append("📋 Pipeline Trace:")
        for step in self.trace:
            lines.append(f"  ├── {step['step']}: {step['value']}")
        
        lines.append("")
        lines.append("📊 Answer:")
        lines.append(f"  {result['answer'][:300]}")
        if len(result['answer']) > 300:
            lines.append("  ...")
        lines.append("=" * 50)
        
        return "\n".join(lines)
