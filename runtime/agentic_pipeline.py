"""
SOCA Agentic Pipeline v22.1 - Fixed Synthesis Integration
"""

import sys
import time
import json
import os
import uuid
from collections import Counter
sys.path.append('runtime')
from soca_runtime import SOCARuntime

GOAL_TTL = 86400
REFLECTION_THRESHOLD = 0.7
MAX_ITERATIONS = 3
RETRIEVAL_STRATEGIES = ['bm25', 'semantic', 'hybrid', 'deep']

class AgenticPipeline:
    def __init__(self):
        self.runtime = SOCARuntime()
        self.trace = []
        self.conversation_state = {}
        self.slot_schema = self._load_slot_schema()
        self.repair_history = {}
        self.strategy_effectiveness = {}

    def _load_slot_schema(self) -> dict:
        schema_path = os.path.expanduser("~/soca/data/schemas/slot_schema.json")
        if os.path.exists(schema_path):
            try:
                with open(schema_path, 'r') as f:
                    return json.load(f)
            except:
                pass
        return {}

    def process(self, query: str, user_id: str = "anonymous") -> dict:
        start_time = time.time()
        self.trace = []

        self._load_conversation_state(user_id)
        self._ensure_goal_stack(user_id)
        self._clean_expired_goals(user_id)

        waiting_goal = self._peek_goal(user_id)
        if waiting_goal and waiting_goal.get("status") == "waiting_for_clarification":
            extracted = self._extract_slots(query)
            filled = self._try_fill_slots(extracted, waiting_goal)
            if filled:
                if waiting_goal.get("status") == "ready":
                    return self._execute_goal_with_reflection(user_id, start_time)
                else:
                    return self._ask_clarification(user_id, waiting_goal, start_time)

        return self._push_new_goal(query, user_id, start_time)

    def _ensure_goal_stack(self, user_id: str):
        if user_id not in self.conversation_state:
            self.conversation_state[user_id] = {}
        if "goal_stack" not in self.conversation_state[user_id]:
            self.conversation_state[user_id]["goal_stack"] = []

    def _peek_goal(self, user_id: str) -> dict:
        stack = self.conversation_state.get(user_id, {}).get("goal_stack", [])
        if stack:
            return stack[-1]
        return None

    def _push_goal(self, user_id: str, goal: dict):
        self.conversation_state[user_id]["goal_stack"].append(goal)
        self._save_conversation_state(user_id)

    def _pop_goal(self, user_id: str) -> dict:
        stack = self.conversation_state.get(user_id, {}).get("goal_stack", [])
        if stack:
            goal = stack.pop()
            self._save_conversation_state(user_id)
            return goal
        return None

    def _clean_expired_goals(self, user_id: str):
        stack = self.conversation_state.get(user_id, {}).get("goal_stack", [])
        if stack:
            goal = stack[-1]
            created_at = goal.get("created_at", 0)
            if time.time() - created_at > GOAL_TTL:
                stack.pop()
                self._save_conversation_state(user_id)

    def _extract_slots(self, query: str) -> dict:
        result = self._execute("sutra_081", {"query": query})
        if result.get("status") == "success":
            return result.get("outputs", {}).get("slots", {})
        return {}

    def _try_fill_slots(self, extracted: dict, goal: dict) -> bool:
        filled = False
        for slot, value in extracted.items():
            if value and not goal.get("filled_slots", {}).get(slot):
                if slot in goal.get("required_slots", []) or slot in goal.get("optional_slots", []):
                    goal["filled_slots"][slot] = value
                    filled = True

        if filled:
            required = goal.get("required_slots", [])
            all_filled = all(goal["filled_slots"].get(slot) for slot in required if slot)
            if all_filled:
                goal["status"] = "ready"
            else:
                goal["status"] = "waiting_for_clarification"
            self._save_conversation_state(goal.get("user_id"))
            return True
        return False

    def _ask_clarification(self, user_id: str, goal: dict, start_time: float) -> dict:
        missing = [s for s in goal.get("required_slots", []) if not goal["filled_slots"].get(s)]
        questions = self._generate_questions(missing, goal.get("intent"))
        return {
            "status": "needs_clarification",
            "questions": questions,
            "missing_slots": missing,
            "goal_id": goal.get("id"),
            "query": goal.get("original_query"),
            "intent": goal.get("intent"),
            "trace": self.trace,
            "elapsed_ms": round((time.time() - start_time) * 1000, 1)
        }

    def _push_new_goal(self, query: str, user_id: str, start_time: float) -> dict:
        working_memory = self._init_working_memory(query, user_id)

        extracted = self._extract_slots(query)
        intent = extracted.get("intent")
        if not intent:
            self._classify_intent(query, working_memory)
            intent = working_memory.get("intent", "general")
        else:
            working_memory["intent"] = intent

        # Goal decomposition
        subgoals = self._decompose_goal(intent, working_memory)
        working_memory["subgoals"] = subgoals

        schema = self.slot_schema.get(intent, {})
        required_slots = schema.get("required", [])
        optional_slots = schema.get("optional", [])
        all_slots = required_slots + optional_slots

        for slot in all_slots:
            if slot not in working_memory["pending_slots"]:
                working_memory["pending_slots"][slot] = None

        for slot, value in extracted.items():
            if value and slot in all_slots:
                working_memory["pending_slots"][slot] = value

        self._load_profile(user_id, working_memory)
        self._load_observation_memory(user_id, working_memory)

        missing = [s for s in required_slots if not working_memory["pending_slots"].get(s)]

        if missing:
            goal = {
                "id": str(uuid.uuid4()),
                "user_id": user_id,
                "intent": intent,
                "original_query": query,
                "required_slots": required_slots,
                "optional_slots": optional_slots,
                "filled_slots": working_memory["pending_slots"].copy(),
                "missing_slots": missing,
                "status": "waiting_for_clarification",
                "created_at": time.time(),
                "iteration": 0,
                "last_confidence": 0.0,
                "evidence": {},
                "actions": [],
                "weaknesses": [],
                "repairs_applied": [],
                "retrieval_strategy": "bm25",
                "repair_history": [],
                "modified_sequence": [],
                "subgoals": subgoals,
                "subgoal_results": {}
            }
            self._push_goal(user_id, goal)
            return self._ask_clarification(user_id, goal, start_time)

        goal = {
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "intent": intent,
            "original_query": query,
            "required_slots": required_slots,
            "optional_slots": optional_slots,
            "filled_slots": working_memory["pending_slots"].copy(),
            "missing_slots": [],
            "status": "ready",
            "created_at": time.time(),
            "iteration": 0,
            "last_confidence": 0.0,
            "evidence": {},
            "actions": [],
            "weaknesses": [],
            "repairs_applied": [],
            "retrieval_strategy": "bm25",
            "repair_history": [],
            "modified_sequence": [],
            "subgoals": subgoals,
            "subgoal_results": {}
        }
        self._push_goal(user_id, goal)
        return self._execute_goal_with_reflection(user_id, start_time)

    def _decompose_goal(self, intent: str, working_memory: dict) -> list:
        """Decompose a goal into subgoals."""
        if intent == 'agriculture':
            subgoals = []
            if not working_memory.get("pending_slots", {}).get("soil_type"):
                subgoals.append({"name": "soil_analysis", "status": "pending"})
            if not working_memory.get("pending_slots", {}).get("season"):
                subgoals.append({"name": "season_check", "status": "pending"})
            if not working_memory.get("pending_slots", {}).get("district"):
                subgoals.append({"name": "district_analysis", "status": "pending"})
            return subgoals
        return []

    def _execute_subgoals(self, goal: dict, working_memory: dict):
        """Execute subgoals and store results."""
        subgoals = goal.get("subgoals", [])
        results = goal.get("subgoal_results", {})

        for subgoal in subgoals:
            name = subgoal.get("name")
            if name not in results:
                if name == "soil_analysis":
                    soil = working_memory.get("pending_slots", {}).get("soil_type", "loamy")
                    results[name] = {"suitability": 0.8, "soil_type": soil}
                elif name == "season_check":
                    season = working_memory.get("pending_slots", {}).get("season", "kharif")
                    results[name] = {"viability": 0.9, "season": season}
                elif name == "district_analysis":
                    district = working_memory.get("pending_slots", {}).get("district", "bongaigaon")
                    results[name] = {"ranking": {"rice": 0.9, "tea": 0.7, "jute": 0.6}}
                subgoal["status"] = "completed"

        goal["subgoal_results"] = results
        return results

    def _execute_goal_with_reflection(self, user_id: str, start_time: float) -> dict:
        goal = self._peek_goal(user_id)
        if not goal:
            return {"status": "failure", "error": "No active goal"}

        best_result = None
        best_confidence = 0.0
        previous_confidence = 0.0
        attempted_actions = set()

        for iteration in range(MAX_ITERATIONS):
            goal["iteration"] = iteration + 1

            working_memory = self._init_working_memory(goal.get("original_query"), user_id)
            working_memory["intent"] = goal.get("intent")
            working_memory["pending_slots"] = goal.get("filled_slots", {}).copy()
            working_memory["profile"] = self._load_profile_only(user_id)
            working_memory["required_slots"] = goal.get("required_slots", [])
            working_memory["retrieval_strategy"] = goal.get("retrieval_strategy", "bm25")
            working_memory["subgoals"] = goal.get("subgoals", [])
            self._load_observation_memory(user_id, working_memory)

            subgoal_results = self._execute_subgoals(goal, working_memory)
            working_memory["subgoal_results"] = subgoal_results

            self._apply_repair_actions(goal, working_memory)

            result = self._execute_full_reasoning(working_memory, start_time)

            # Structured Critic
            critic_result = self._execute("sutra_083", {
                "answer": result.get("answer", ""),
                "sources": result.get("sources", []),
                "slots": working_memory.get("pending_slots", {}),
                "intent": working_memory.get("intent", "general")
            })

            weaknesses = []
            actions = []
            critic_score = 0.5
            if critic_result.get("status") == "success":
                weaknesses = critic_result.get("outputs", {}).get("weaknesses", [])
                actions = critic_result.get("outputs", {}).get("actions", [])
                critic_score = critic_result.get("outputs", {}).get("quality", 0.5)
                goal["weaknesses"] = weaknesses
                goal["actions"] = actions
                self._save_conversation_state(user_id)

            evidence = self._build_evidence_graph(result, working_memory)
            goal["evidence"] = evidence

            diversity_score = self._calculate_diversity_score(result.get("sources", []))

            base_confidence = self._calculate_dynamic_confidence(working_memory, result)
            confidence = base_confidence * (0.5 + 0.3 * critic_score + 0.2 * diversity_score)
            confidence = min(1.0, confidence)
            result["confidence"] = confidence

            strategy = working_memory.get("retrieval_strategy", "bm25")
            self._track_strategy_effectiveness(strategy, confidence)

            delta = confidence - previous_confidence
            if iteration > 0:
                goal["repair_history"].append({
                    "iteration": iteration,
                    "delta": delta,
                    "action": goal.get("last_action", "none"),
                    "confidence": confidence,
                    "critic_score": critic_score,
                    "strategy": strategy
                })

            if confidence > best_confidence:
                best_confidence = confidence
                best_result = result

            goal["last_confidence"] = confidence
            goal["evidence"] = evidence
            previous_confidence = confidence

            if confidence >= REFLECTION_THRESHOLD and len(weaknesses) == 0:
                self._save_observation_memory(user_id, working_memory)
                self._pop_goal(user_id)
                result["iteration"] = iteration + 1
                result["critic_used"] = True
                return result

            if iteration < MAX_ITERATIONS - 1 and actions:
                new_actions = [a for a in actions if str(a) not in attempted_actions]
                if new_actions:
                    executed = self._execute_actions(goal, working_memory, new_actions)
                    if executed:
                        attempted_actions.update(str(a) for a in new_actions)
                        goal["last_action"] = new_actions[0].get("type", "unknown")
                        self._save_conversation_state(user_id)
                        continue

        self._save_observation_memory(user_id, working_memory)
        self._pop_goal(user_id)
        if best_result:
            best_result["iteration"] = goal.get("iteration", MAX_ITERATIONS)
            best_result["critic_used"] = True
            return best_result

        return result

    def _build_evidence_graph(self, result: dict, working_memory: dict) -> dict:
        sources = result.get("sources", [])
        answer = result.get("answer", "")

        claims = []
        if "rice" in answer.lower():
            claims.append({"claim": "Rice is suitable", "evidence": sources})
        if "tea" in answer.lower():
            claims.append({"claim": "Tea is suitable", "evidence": sources})
        if "jute" in answer.lower():
            claims.append({"claim": "Jute is suitable", "evidence": sources})

        return {
            "claims": claims,
            "source_count": len(sources),
            "unique_sources": list(set(sources)),
            "diversity_score": self._calculate_diversity_score(sources)
        }

    def _calculate_diversity_score(self, sources: list) -> float:
        if not sources:
            return 0.0

        source_types = []
        for s in sources:
            if "crop" in s or "agriculture" in s:
                source_types.append("crop")
            elif "weather" in s or "climate" in s:
                source_types.append("weather")
            elif "market" in s or "price" in s:
                source_types.append("market")
            else:
                source_types.append("other")

        unique_types = len(set(source_types))
        diversity = min(1.0, unique_types / 3.0)
        return diversity

    def _track_strategy_effectiveness(self, strategy: str, confidence: float):
        if strategy not in self.strategy_effectiveness:
            self.strategy_effectiveness[strategy] = []
        self.strategy_effectiveness[strategy].append(confidence)

    def _execute_actions(self, goal: dict, working_memory: dict, actions: list) -> bool:
        executed = False

        for action in actions:
            action_type = action.get("type", "")

            if action_type == "ask":
                slot = action.get("slot", "")
                if slot:
                    missing_slots = goal.get("missing_slots", [])
                    if slot not in missing_slots:
                        missing_slots.append(slot)
                        goal["missing_slots"] = missing_slots
                        goal["status"] = "waiting_for_clarification"
                        self._save_conversation_state(goal.get("user_id"))
                        return True

            elif action_type == "retrieve":
                strategy = action.get("strategy", "semantic")
                goal["retrieval_strategy"] = strategy
                executed = True

            elif action_type == "specific" or action_type == "expand":
                if goal.get("intent") == "agriculture":
                    if "sutra_056" not in goal.get("modified_sequence", []):
                        goal["modified_sequence"] = goal.get("modified_sequence", []) + ["sutra_056"]
                executed = True

        if executed:
            goal["repairs_applied"] = goal.get("repairs_applied", []) + actions

        return executed

    def _apply_repair_actions(self, goal: dict, working_memory: dict):
        for action in goal.get("repairs_applied", []):
            action_type = action.get("type", "")
            if action_type == "retrieve":
                working_memory["retrieval_strategy"] = goal.get("retrieval_strategy", "bm25")
            if action_type == "specific":
                working_memory["modified_sequence"] = goal.get("modified_sequence", [])

    def _calculate_dynamic_confidence(self, working_memory: dict, result: dict) -> float:
        required_slots = working_memory.get("required_slots", [])
        pending_slots = working_memory.get("pending_slots", {})

        if required_slots:
            filled = sum(1 for s in required_slots if pending_slots.get(s))
            slot_score = filled / len(required_slots)
        else:
            slot_score = 0.5

        fact_result = self._execute("sutra_071", {
            "answer": result.get("answer", ""),
            "sources": result.get("sources", []),
            "domain": working_memory.get("intent", "general")
        })
        fact_conf = fact_result.get("confidence", 0.5) if fact_result.get("status") == "success" else 0.5

        quality_result = self._execute("sutra_079", {
            "answer": result.get("answer", ""),
            "sources": result.get("sources", []),
            "ranked_results": working_memory.get("ranked_knowledge", []),
            "domain": working_memory.get("intent", "general")
        })
        quality_conf = quality_result.get("outputs", {}).get("quality_score", 0.5) if quality_result.get("status") == "success" else 0.5

        confidence = slot_score * 0.3 + fact_conf * 0.35 + quality_conf * 0.35
        return min(1.0, confidence)

    def _load_profile_only(self, user_id: str) -> dict:
        profile_result = self._execute("sutra_076", {"action": "load", "user_id": user_id})
        if profile_result.get("status") == "success":
            return profile_result.get("outputs", {}).get("profile", {})
        return {}

    def _load_profile(self, user_id: str, working_memory: dict):
        profile = self._load_profile_only(user_id)
        working_memory["profile"] = profile
        if profile.get("district") and not working_memory["pending_slots"].get("district"):
            working_memory["pending_slots"]["district"] = profile["district"]
        if profile.get("soil_type") and not working_memory["pending_slots"].get("soil_type"):
            working_memory["pending_slots"]["soil_type"] = profile["soil_type"]

    def _load_observation_memory(self, user_id: str, working_memory: dict):
        state = self.conversation_state.get(user_id, {})
        obs = state.get("observations", {})
        if obs.get("district") and not working_memory["pending_slots"].get("district"):
            working_memory["pending_slots"]["district"] = obs["district"]
        if obs.get("soil_type") and not working_memory["pending_slots"].get("soil_type"):
            working_memory["pending_slots"]["soil_type"] = obs["soil_type"]
        if obs.get("last_crop"):
            working_memory["last_crop"] = obs["last_crop"]

    def _save_observation_memory(self, user_id: str, working_memory: dict):
        obs = {}
        if working_memory.get("pending_slots", {}).get("district"):
            obs["district"] = working_memory["pending_slots"]["district"]
        if working_memory.get("pending_slots", {}).get("soil_type"):
            obs["soil_type"] = working_memory["pending_slots"]["soil_type"]
        if working_memory.get("last_crop"):
            obs["last_crop"] = working_memory["last_crop"]
        if obs:
            self.conversation_state[user_id]["observations"] = obs
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
            "evidence": {},
            "results": {},
            "synthesis": "",
            "confidence": 0.5,
            "approved": False,
            "sources": [],
            "trace": [],
            "pending_slots": {},
            "required_slots": [],
            "iteration": 0,
            "goal_reached": False,
            "observations": [],
            "actions": [],
            "last_crop": None,
            "retrieval_strategy": "bm25",
            "modified_sequence": [],
            "subgoals": [],
            "subgoal_results": {}
        }

    def _classify_intent(self, query: str, working_memory: dict):
        intent_result = self._execute("sutra_045", {"query": query})
        if intent_result.get("status") == "success":
            working_memory["intent"] = intent_result.get("outputs", {}).get("intent", "general")
        self._add_trace("intent", working_memory["intent"])

    def _generate_questions(self, missing: list, intent: str = "general") -> list:
        schema = self.slot_schema.get(intent, {})
        questions = schema.get("questions", {})
        return [questions.get(slot, f"What is the {slot}?") for slot in missing]

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
        retrieval_strategy = working_memory.get("retrieval_strategy", "bm25")
        self._add_trace("retrieval", retrieval_strategy)

        knowledge_result = self._execute("sutra_074", {
            "query": working_memory["query"],
            "district": working_memory["pending_slots"].get("district", ""),
            "crop": "",
            "strategy": retrieval_strategy
        })
        if knowledge_result.get("status") == "success":
            working_memory["knowledge"] = knowledge_result.get("outputs", {}).get("knowledge_results", [])
        self._add_trace("knowledge", len(working_memory["knowledge"]))

        ranker_result = self._execute("sutra_080", {
            "query": working_memory["query"],
            "knowledge_results": working_memory["knowledge"],
            "top_k": 5
        })
        if ranker_result.get("status") == "success":
            working_memory["ranked_knowledge"] = ranker_result.get("outputs", {}).get("ranked_results", [])
        self._add_trace("bm25", len(working_memory["ranked_knowledge"]))

        planner_result = self._execute("sutra_069", {
            "query": working_memory["query"],
            "intent": working_memory["intent"]
        })
        sequence = planner_result.get("outputs", {}).get("sequence", ["sutra_041"])

        if working_memory.get("modified_sequence"):
            sequence = sequence + working_memory["modified_sequence"]

        results = {}
        domain_sources = []
        for sutra_id in sequence:
            if sutra_id in ["sutra_068", "sutra_069", "sutra_070", "sutra_071", "sutra_072",
                           "sutra_073", "sutra_074", "sutra_075", "sutra_076", "sutra_077",
                           "sutra_078", "sutra_079", "sutra_080", "sutra_081", "sutra_082",
                           "sutra_083", "sutra_084"]:
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
                # Collect sources
                if "sources" in outputs:
                    domain_sources.extend(outputs.get("sources", []))
                for k, v in outputs.items():
                    if v not in [None, "", []]:
                        if isinstance(v, str):
                            v = v.strip()
                        if k not in working_memory["results"]:
                            working_memory["results"][k] = []
                        if isinstance(v, list):
                            for item in v:
                                item_str = str(item).strip().lower()
                                if not any(str(existing).strip().lower() == item_str for existing in working_memory["results"][k]):
                                    working_memory["results"][k].append(item)
                        else:
                            v_str = str(v).strip().lower()
                            if not any(str(existing).strip().lower() == v_str for existing in working_memory["results"][k]):
                                working_memory["results"][k].append(v)

        self._add_trace("domain", len(results))

        # Use Synthesis Engine (sutra_084)
        synthesis_result = self._execute("sutra_084", {
            "results": working_memory.get("results", {}),
            "slots": working_memory.get("pending_slots", {}),
            "intent": working_memory.get("intent", "general"),
            "sources": domain_sources,
            "subgoals": working_memory.get("subgoal_results", {})
        })

        synthesis = ""
        recommendation = ""
        ranked_crops = []
        alternatives = []
        sources = []

        if synthesis_result.get("status") == "success":
            synthesis = synthesis_result.get("outputs", {}).get("synthesis", "")
            recommendation = synthesis_result.get("outputs", {}).get("recommendation", "")
            ranked_crops = synthesis_result.get("outputs", {}).get("ranked_crops", [])
            alternatives = synthesis_result.get("outputs", {}).get("alternatives", [])
            sources = synthesis_result.get("outputs", {}).get("sources", [])
            working_memory["synthesis"] = synthesis
            working_memory["sources"] = sources
        else:
            # Fallback to old reasoner if synthesis fails
            reasoner_result = self._execute("sutra_070", {
                "results": results,
                "query": working_memory["query"],
                "context": working_memory["context"],
                "ranked_knowledge": working_memory["ranked_knowledge"]
            })
            if reasoner_result.get("status") == "success":
                synthesis = reasoner_result.get("outputs", {}).get("synthesis", "")
                sources = reasoner_result.get("outputs", {}).get("sources", [])
                working_memory["synthesis"] = synthesis
                working_memory["sources"] = sources

        self._add_trace("synthesis", synthesis[:50])

        elapsed = time.time() - start_time

        return {
            "status": "success",
            "query": working_memory["query"],
            "intent": working_memory["intent"],
            "answer": synthesis,
            "synthesis": synthesis,
            "recommendation": recommendation,
            "ranked_crops": ranked_crops,
            "alternatives": alternatives,
            "confidence": 0.5,
            "approved": False,
            "sources": sources,
            "profile": working_memory["profile"],
            "context": working_memory["context"],
            "slots_filled": working_memory["pending_slots"],
            "ranked_knowledge": working_memory["ranked_knowledge"][:3],
            "trace": self.trace,
            "iteration": working_memory.get("iteration", 1),
            "retrieval_strategy": working_memory.get("retrieval_strategy", "bm25"),
            "subgoal_results": working_memory.get("subgoal_results", {}),
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
            f"🔍 Strategy: {result.get('retrieval_strategy', 'bm25')}",
            "",
            "📋 Slots Filled:"
        ]
        for k, v in result.get('slots_filled', {}).items():
            if v:
                lines.append(f"  ├── {k}: {v}")

        lines.append("")
        if result.get('recommendation'):
            lines.append("📊 Recommendation:")
            lines.append(f"  {result['recommendation']}")

        if result.get('alternatives'):
            lines.append("")
            lines.append("📊 Alternatives:")
            for alt in result['alternatives']:
                lines.append(f"  ├── {alt}")

        lines.append("")
        lines.append("📊 Answer:")
        lines.append(f"  {result['answer'][:300]}")
        if len(result['answer']) > 300:
            lines.append("  ...")
        lines.append("=" * 50)

        return "\n".join(lines)
