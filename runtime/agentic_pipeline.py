"""
SOCA Agentic Pipeline v13.0 - Multi-Goal Agent with Planner-Driven Slots
"""

import sys
import time
import re
import json
import os
import uuid
from collections import Counter
sys.path.append('runtime')
from soca_runtime import SOCARuntime

# Goal expiration (24 hours)
GOAL_TTL = 86400

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
        
        # Clean expired goals
        self._clean_expired_goals(user_id)
        
        # Check if there's an active goal waiting for clarification
        active_goal = self._get_active_goal(user_id)
        
        if active_goal and active_goal.get("status") == "waiting_for_clarification":
            # Try to fill the missing slot with the query
            filled = self._try_fill_slot(query, active_goal)
            if filled:
                # Resume the goal
                return self._resume_goal(user_id, active_goal, start_time)
        
        # Start a new goal
        return self._start_new_goal(query, user_id, start_time)
    
    def _clean_expired_goals(self, user_id: str):
        """Remove expired goals."""
        state = self.conversation_state.get(user_id, {})
        active_goal = state.get("active_goal")
        if active_goal:
            created_at = active_goal.get("created_at", 0)
            if time.time() - created_at > GOAL_TTL:
                state["active_goal"] = None
                self._save_conversation_state(user_id)
    
    def _get_active_goal(self, user_id: str) -> dict:
        """Get the active goal for a user."""
        state = self.conversation_state.get(user_id, {})
        return state.get("active_goal", None)
    
    def _try_fill_slot(self, query: str, goal: dict) -> bool:
        """Try to fill a missing slot from the query."""
        query_lower = query.lower()
        slots_filled = False
        
        # Check for season
        seasons = {"kharif": "kharif", "rabi": "rabi", "summer": "summer", "winter": "winter",
                   "monsoon": "kharif", "rainy": "kharif"}
        for key, value in seasons.items():
            if key in query_lower and not goal.get("filled_slots", {}).get("season"):
                goal["filled_slots"]["season"] = value
                slots_filled = True
                break
        
        # Check for district
        districts = ["bongaigaon", "barpeta", "jorhat", "nagaon", "dibrugarh",
                    "sonitpur", "dhubri", "goalpara", "kokrajhar", "tinsukia"]
        for district in districts:
            if district in query_lower and not goal.get("filled_slots", {}).get("district"):
                goal["filled_slots"]["district"] = district
                slots_filled = True
                break
        
        # Check for soil
        soils = ["loamy", "clay", "sandy", "alluvial"]
        for soil in soils:
            if soil in query_lower and not goal.get("filled_slots", {}).get("soil_type"):
                goal["filled_slots"]["soil_type"] = soil
                slots_filled = True
                break
        
        if slots_filled:
            required = goal.get("required_slots", [])
            all_filled = all(goal.get("filled_slots", {}).get(slot) for slot in required)
            if all_filled:
                goal["status"] = "ready"
            else:
                goal["status"] = "waiting_for_clarification"
            self._save_conversation_state(goal.get("user_id"))
            return True
        
        return False
    
    def _start_new_goal(self, query: str, user_id: str, start_time: float) -> dict:
        """Start a new goal."""
        # Initialize working memory
        working_memory = self._init_working_memory(query, user_id)
        
        # Fill slots from query
        self._fill_slots_from_query(query, working_memory)
        
        # Load profile (fill district and soil_type, but NOT season)
        self._load_profile(user_id, working_memory)
        
        # Load observation memory
        self._load_observation_memory(user_id, working_memory)
        
        # Classify intent
        self._classify_intent(query, working_memory)
        
        # Get required slots from planner (sutra_069)
        planner_result = self._execute("sutra_069", {
            "query": query,
            "intent": working_memory["intent"]
        })
        required_slots = planner_result.get("outputs", {}).get("required_slots", ["season"])
        
        # If agriculture, ensure season is always required
        if working_memory.get("intent") == "agriculture" and "season" not in required_slots:
            required_slots.append("season")
        
        # Check if all required slots are filled
        all_filled = all(working_memory["pending_slots"].get(slot) for slot in required_slots)
        
        if not all_filled:
            # Create a goal
            goal = {
                "id": str(uuid.uuid4()),
                "user_id": user_id,
                "intent": working_memory["intent"],
                "original_query": query,
                "required_slots": required_slots,
                "filled_slots": working_memory["pending_slots"].copy(),
                "status": "waiting_for_clarification",
                "created_at": time.time()
            }
            
            # Save goal
            self.conversation_state[user_id]["active_goal"] = goal
            self._save_conversation_state(user_id)
            
            # Generate questions for missing slots
            missing = [slot for slot in required_slots if not working_memory["pending_slots"].get(slot)]
            questions = self._generate_questions(missing)
            
            return {
                "status": "needs_clarification",
                "questions": questions,
                "missing_slots": missing,
                "goal_id": goal["id"],
                "query": query,
                "intent": working_memory["intent"],
                "trace": self.trace,
                "elapsed_ms": round((time.time() - start_time) * 1000, 1)
            }
        
        # All slots filled, execute reasoning
        return self._execute_full_reasoning(working_memory, start_time)
    
    def _resume_goal(self, user_id: str, goal: dict, start_time: float) -> dict:
        """Resume a goal after slots are filled."""
        # Build working memory from goal
        working_memory = self._init_working_memory(goal.get("original_query"), user_id)
        working_memory["intent"] = goal.get("intent")
        working_memory["pending_slots"] = goal.get("filled_slots", {}).copy()
        working_memory["profile"] = self._load_profile_only(user_id)
        self._load_observation_memory(user_id, working_memory)
        
        # Mark as executing
        goal["status"] = "executing"
        self._save_conversation_state(user_id)
        
        # Execute reasoning
        result = self._execute_full_reasoning(working_memory, start_time)
        
        # Clear the active goal after successful execution
        self.conversation_state[user_id]["active_goal"] = None
        # Store in goal history
        if "goal_history" not in self.conversation_state[user_id]:
            self.conversation_state[user_id]["goal_history"] = []
        self.conversation_state[user_id]["goal_history"].append({
            "goal_id": goal.get("id"),
            "query": goal.get("original_query"),
            "result": result.get("answer", "")[:100],
            "completed_at": time.time()
        })
        # Keep only last 10 goals
        if len(self.conversation_state[user_id]["goal_history"]) > 10:
            self.conversation_state[user_id]["goal_history"] = self.conversation_state[user_id]["goal_history"][-10:]
        self._save_conversation_state(user_id)
        
        return result
    
    def _load_observation_memory(self, user_id: str, working_memory: dict):
        """Load observation memory and fill slots."""
        state = self.conversation_state.get(user_id, {})
        observations = state.get("observations", {})
        
        # Fill from observations if not already set
        if observations.get("district") and not working_memory["pending_slots"].get("district"):
            working_memory["pending_slots"]["district"] = observations["district"]
            working_memory["context"]["district"] = observations["district"]
        
        if observations.get("soil_type") and not working_memory["pending_slots"].get("soil_type"):
            working_memory["pending_slots"]["soil_type"] = observations["soil_type"]
        
        if observations.get("last_crop") and not working_memory.get("last_crop"):
            working_memory["last_crop"] = observations["last_crop"]
    
    def _save_observation_memory(self, user_id: str, working_memory: dict):
        """Save observation memory from working memory."""
        observations = {}
        if working_memory.get("pending_slots", {}).get("district"):
            observations["district"] = working_memory["pending_slots"]["district"]
        if working_memory.get("pending_slots", {}).get("soil_type"):
            observations["soil_type"] = working_memory["pending_slots"]["soil_type"]
        if working_memory.get("last_crop"):
            observations["last_crop"] = working_memory["last_crop"]
        
        if observations:
            self.conversation_state[user_id]["observations"] = observations
            self._save_conversation_state(user_id)
    
    def _init_working_memory(self, query: str, user_id: str) -> dict:
        return {
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
            "last_crop": None
        }
    
    def _load_profile_only(self, user_id: str) -> dict:
        """Load profile without modifying working memory."""
        profile_result = self._execute("sutra_076", {"action": "load", "user_id": user_id})
        if profile_result.get("status") == "success":
            return profile_result.get("outputs", {}).get("profile", {})
        return {}
    
    def _classify_intent(self, query: str, working_memory: dict):
        intent_result = self._execute("sutra_045", {"query": query})
        if intent_result.get("status") == "success":
            working_memory["intent"] = intent_result.get("outputs", {}).get("intent", "general")
            working_memory["context"]["intent"] = working_memory["intent"]
        self._add_trace("intent", working_memory["intent"])
    
    def _fill_slots_from_query(self, query: str, working_memory: dict):
        query_lower = query.lower()
        
        # State
        if "assam" in query_lower or "axom" in query_lower:
            working_memory["context"]["state"] = "assam"
        
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
        
        # Season (with synonyms)
        seasons = {"kharif": "kharif", "rabi": "rabi", "summer": "summer", "winter": "winter",
                   "monsoon": "kharif", "rainy": "kharif"}
        for key, value in seasons.items():
            if key in query_lower:
                working_memory["pending_slots"]["season"] = value
                working_memory["context"]["season"] = value
                break
        
        # Soil
        soils = ["loamy", "clay", "sandy", "alluvial"]
        for soil in soils:
            if soil in query_lower:
                working_memory["pending_slots"]["soil_type"] = soil
                break
    
    def _load_profile(self, user_id: str, working_memory: dict):
        profile = self._load_profile_only(user_id)
        working_memory["profile"] = profile
        
        # Fill district and soil_type from profile (but NOT season)
        if profile.get("district") and not working_memory["pending_slots"].get("district"):
            working_memory["pending_slots"]["district"] = profile["district"]
            working_memory["context"]["district"] = profile["district"]
        
        if profile.get("soil_type") and not working_memory["pending_slots"].get("soil_type"):
            working_memory["pending_slots"]["soil_type"] = profile["soil_type"]
    
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
        knowledge_score = min(1.0, len(working_memory["ranked_knowledge"]) * 0.05)
        confidence = round((slot_score * 0.4 + source_score * 0.2 + knowledge_score * 0.2 + 0.2), 2)
        confidence = min(1.0, confidence)
        
        # Response Validator
        validator_result = self._execute("sutra_072", {
            "response": working_memory["synthesis"],
            "confidence": confidence,
            "sources": working_memory["sources"]
        })
        if validator_result.get("status") == "success":
            working_memory["approved"] = validator_result.get("outputs", {}).get("approved", False)
        
        # Save observation memory
        self._save_observation_memory(working_memory["user_id"], working_memory)
        
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
