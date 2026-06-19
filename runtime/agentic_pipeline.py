"""
SOCA Agentic Pipeline v11.0 - Goal Stack + Task Resumption
"""

import sys
import time
import re
import json
import os
from collections import Counter
sys.path.append('runtime')
from soca_runtime import SOCARuntime

class AgenticPipeline:
    def __init__(self):
        self.runtime = SOCARuntime()
        self.trace = []
        self.max_iterations = 3
        self.conversation_state = {}
    
    def process(self, query: str, user_id: str = "anonymous") -> dict:
        start_time = time.time()
        self.trace = []
        
        # Load conversation state
        self._load_conversation_state(user_id)
        
        # Check if this is a continuation (slot fill)
        is_continuation = self._is_slot_fill(query)
        
        if is_continuation and self.conversation_state.get(user_id, {}).get("goal"):
            # Resume the goal
            return self._resume_goal(query, user_id, start_time)
        
        # Otherwise, start new goal
        return self._start_new_goal(query, user_id, start_time)
    
    def _is_slot_fill(self, query: str) -> bool:
        """Check if query is filling a slot."""
        query_lower = query.lower()
        # Check if it's a season, district, or soil type
        seasons = ["kharif", "rabi", "summer", "winter"]
        districts = ["bongaigaon", "barpeta", "jorhat", "nagaon", "dibrugarh",
                    "sonitpur", "dhubri", "goalpara", "kokrajhar", "tinsukia"]
        soils = ["loamy", "clay", "sandy", "alluvial"]
        
        for word in seasons + districts + soils:
            if word in query_lower:
                return True
        return False
    
    def _start_new_goal(self, query: str, user_id: str, start_time: float) -> dict:
        """Start a new goal from query."""
        # Initialize working memory
        working_memory = {
            "query": query,
            "user_id": user_id,
            "language": "en",
            "intent": None,
            "profile": {},
            "context": {"state": None},
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
            "goal_reached": False,
            "observations": [],
            "actions": [],
            "goal": {
                "task": "crop_recommendation",
                "status": "pending"
            }
        }
        
        # Fill slots from query
        self._fill_slots_from_query(query, working_memory)
        
        # Load profile
        self._load_profile(user_id, working_memory)
        
        # Restore pending slots from conversation state
        if user_id in self.conversation_state:
            for slot, value in self.conversation_state[user_id].get("pending_slots", {}).items():
                if value and not working_memory["pending_slots"].get(slot):
                    working_memory["pending_slots"][slot] = value
        
        # Classify intent
        self._classify_intent(query, working_memory)
        
        # Check slots
        if not self._all_slots_filled(working_memory):
            missing = self._get_missing_slots(working_memory)
            # Save goal state
            self.conversation_state[user_id] = {
                "goal": working_memory["goal"],
                "pending_slots": working_memory["pending_slots"],
                "query": query,
                "intent": working_memory["intent"],
                "profile": working_memory["profile"],
                "context": working_memory["context"],
                "iteration": 0
            }
            self._save_conversation_state(user_id)
            
            return {
                "status": "needs_clarification",
                "questions": self._generate_questions(missing),
                "missing_slots": missing,
                "query": query,
                "intent": working_memory["intent"],
                "trace": self.trace,
                "elapsed_ms": round((time.time() - start_time) * 1000, 1)
            }
        
        # All slots filled, execute reasoning
        return self._execute_full_reasoning(working_memory, start_time)
    
    def _resume_goal(self, query: str, user_id: str, start_time: float) -> dict:
        """Resume a goal with a slot fill."""
        state = self.conversation_state.get(user_id, {})
        goal = state.get("goal", {})
        pending_slots = state.get("pending_slots", {})
        
        # Fill the slot from query
        query_lower = query.lower()
        
        # Check for season
        seasons = {"kharif": "kharif", "rabi": "rabi", "summer": "summer", "winter": "winter"}
        for key, value in seasons.items():
            if key in query_lower and not pending_slots.get("season"):
                pending_slots["season"] = value
                break
        
        # Check for district
        districts = ["bongaigaon", "barpeta", "jorhat", "nagaon", "dibrugarh",
                    "sonitpur", "dhubri", "goalpara", "kokrajhar", "tinsukia"]
        for district in districts:
            if district in query_lower and not pending_slots.get("district"):
                pending_slots["district"] = district
                break
        
        # Check for soil
        soils = ["loamy", "clay", "sandy", "alluvial"]
        for soil in soils:
            if soil in query_lower and not pending_slots.get("soil_type"):
                pending_slots["soil_type"] = soil
                break
        
        # Update state
        self.conversation_state[user_id]["pending_slots"] = pending_slots
        
        # Check if all slots are filled
        required = ["season"]
        if state.get("intent") == "agriculture":
            required.append("district")
        
        all_filled = all(pending_slots.get(slot) for slot in required)
        
        if all_filled:
            # Resume reasoning
            working_memory = {
                "query": state.get("query", query),
                "user_id": user_id,
                "language": "en",
                "intent": state.get("intent"),
                "profile": state.get("profile", {}),
                "context": state.get("context", {}),
                "knowledge": [],
                "ranked_knowledge": [],
                "evidence": [],
                "results": {},
                "synthesis": "",
                "confidence": 0.5,
                "approved": False,
                "sources": [],
                "trace": [],
                "pending_slots": pending_slots,
                "iteration": state.get("iteration", 0) + 1,
                "goal_reached": False,
                "observations": [],
                "actions": [],
                "goal": state.get("goal", {})
            }
            
            # Clear the goal state
            self.conversation_state[user_id] = {}
            self._save_conversation_state(user_id)
            
            return self._execute_full_reasoning(working_memory, start_time)
        else:
            # Still missing slots
            missing = []
            for slot in required:
                if not pending_slots.get(slot):
                    missing.append(slot)
            
            self._save_conversation_state(user_id)
            
            return {
                "status": "needs_clarification",
                "questions": self._generate_questions(missing),
                "missing_slots": missing,
                "query": state.get("query", query),
                "intent": state.get("intent"),
                "trace": self.trace,
                "elapsed_ms": round((time.time() - start_time) * 1000, 1)
            }
    
    def _classify_intent(self, query: str, working_memory: dict):
        intent_result = self._execute("sutra_045", {"query": query})
        if intent_result.get("status") == "success":
            working_memory["intent"] = intent_result.get("outputs", {}).get("intent", "general")
            working_memory["context"]["intent"] = working_memory["intent"]
        self._add_trace("intent", working_memory["intent"])
    
    def _fill_slots_from_query(self, query: str, working_memory: dict):
        query_lower = query.lower()
        
        if "assam" in query_lower or "axom" in query_lower:
            working_memory["context"]["state"] = "assam"
        
        districts = ["bongaigaon", "barpeta", "jorhat", "nagaon", "dibrugarh",
                    "sonitpur", "dhubri", "goalpara", "kokrajhar", "tinsukia",
                    "sivasagar", "golaghat", "lakhimpur", "dhemaji", "morigaon",
                    "nalbari", "kamrup", "cachar", "hailakandi", "karimganj",
                    "karbi_anglong", "dima_hasao", "chirang", "udalguri", "baksa"]
        for district in districts:
            if district in query_lower:
                working_memory["pending_slots"]["district"] = district
                working_memory["context"]["district"] = district
                break
        
        seasons = ["kharif", "rabi", "summer", "winter"]
        for season in seasons:
            if season in query_lower:
                working_memory["pending_slots"]["season"] = season
                working_memory["context"]["season"] = season
                break
        
        soils = ["loamy", "clay", "sandy", "alluvial"]
        for soil in soils:
            if soil in query_lower:
                working_memory["pending_slots"]["soil_type"] = soil
                break
    
    def _load_profile(self, user_id: str, working_memory: dict):
        profile_result = self._execute("sutra_076", {
            "action": "load",
            "user_id": user_id
        })
        if profile_result.get("status") == "success":
            profile = profile_result.get("outputs", {}).get("profile", {})
            working_memory["profile"] = profile
            
            if profile.get("district") and not working_memory["pending_slots"]["district"]:
                working_memory["pending_slots"]["district"] = profile["district"]
                working_memory["context"]["district"] = profile["district"]
            
            if profile.get("soil_type") and not working_memory["pending_slots"]["soil_type"]:
                working_memory["pending_slots"]["soil_type"] = profile["soil_type"]
    
    def _all_slots_filled(self, working_memory: dict) -> bool:
        required = ["season"]
        if working_memory.get("intent") == "agriculture":
            required.append("district")
        
        for slot in required:
            if not working_memory["pending_slots"].get(slot):
                return False
        return True
    
    def _get_missing_slots(self, working_memory: dict) -> list:
        missing = []
        if working_memory.get("intent") == "agriculture":
            if not working_memory["pending_slots"].get("district"):
                missing.append("district")
        if not working_memory["pending_slots"].get("season"):
            missing.append("season")
        if not working_memory["pending_slots"].get("soil_type"):
            missing.append("soil_type")
        return missing
    
    def _generate_questions(self, missing: list) -> list:
        questions = []
        for slot in missing:
            if slot == "district":
                questions.append("Which district are you in?")
            elif slot == "season":
                questions.append("Which season are you planning to grow in? (kharif/rabi/summer)")
            elif slot == "soil_type":
                questions.append("What type of soil do you have? (loamy/clay/sandy)")
        return questions
    
    def _load_conversation_state(self, user_id: str):
        state_path = os.path.expanduser(f"~/soca/data/profiles/{user_id}_state.json")
        if os.path.exists(state_path):
            try:
                with open(state_path, 'r') as f:
                    self.conversation_state[user_id] = json.load(f)
            except:
                self.conversation_state[user_id] = {}
        else:
            self.conversation_state[user_id] = {}
    
    def _save_conversation_state(self, user_id: str):
        state_path = os.path.expanduser(f"~/soca/data/profiles/{user_id}_state.json")
        os.makedirs(os.path.dirname(state_path), exist_ok=True)
        with open(state_path, 'w') as f:
            json.dump(self.conversation_state.get(user_id, {}), f, indent=2)
    
    def _execute_full_reasoning(self, working_memory: dict, start_time: float) -> dict:
        # Knowledge Retrieval
        knowledge_result = self._execute("sutra_074", {
            "query": working_memory["query"],
            "district": working_memory["pending_slots"].get("district", ""),
            "crop": ""
        })
        if knowledge_result.get("status") == "success":
            working_memory["knowledge"] = knowledge_result.get("outputs", {}).get("knowledge_results", [])
        self._add_trace("knowledge", len(working_memory["knowledge"]))
        
        # BM25 Ranking
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
        
        # Calculate confidence
        slot_score = self._calculate_slot_confidence(working_memory)
        source_score = min(1.0, len(working_memory["sources"]) * 0.1)
        confidence = round((slot_score * 0.5 + source_score * 0.5), 2)
        
        # Response Validator
        validator_result = self._execute("sutra_072", {
            "response": working_memory["synthesis"],
            "confidence": confidence,
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
            "confidence": confidence,
            "approved": working_memory["approved"],
            "sources": working_memory["sources"],
            "profile": working_memory["profile"],
            "context": working_memory["context"],
            "slots_filled": working_memory["pending_slots"],
            "ranked_knowledge": working_memory["ranked_knowledge"][:3],
            "trace": self.trace,
            "iteration": working_memory.get("iteration", 1),
            "elapsed_ms": round(elapsed * 1000, 1)
        }
    
    def _calculate_slot_confidence(self, working_memory: dict) -> float:
        filled = 0
        total = 0
        for slot, value in working_memory["pending_slots"].items():
            if slot in ["season", "district", "soil_type"]:
                total += 1
                if value:
                    filled += 1
        if total == 0:
            return 0.5
        return filled / total
    
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
        lines.append("📊 Answer:")
        lines.append(f"  {result['answer'][:300]}")
        if len(result['answer']) > 300:
            lines.append("  ...")
        lines.append("=" * 50)
        
        return "\n".join(lines)
