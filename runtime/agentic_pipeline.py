"""
SOCA Agentic Pipeline v8.0 - True Autonomous Agent
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
        
        # Initialize shared working memory
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
            "clarification_needed": False,
            "clarification_questions": []
        }
        
        # Step 1: Extract location and season from query
        location = self._extract_location(query)
        if location:
            working_memory["context"]["location"] = location
            working_memory["context"]["district"] = location
        
        season = self._extract_season(query)
        if season:
            working_memory["context"]["season"] = season
        
        # Step 2: Load profile (sutra_076)
        profile_result = self._execute("sutra_076", {
            "action": "load",
            "user_id": user_id
        })
        if profile_result.get("status") == "success":
            profile = profile_result.get("outputs", {}).get("profile", {})
            working_memory["profile"] = profile
            working_memory["profile_loaded"] = profile_result.get("outputs", {}).get("profile_loaded", False)
            
            # FIX: Override context with profile district
            if profile.get("district") and profile["district"] not in ["", "bongaigaon"]:
                working_memory["context"]["district"] = profile["district"]
                working_memory["context"]["location"] = profile["district"]
            elif profile.get("district") == "bongaigaon" and not working_memory["context"].get("district"):
                working_memory["context"]["district"] = "bongaigaon"
        
        # Step 3: Intent Classification (sutra_045)
        intent_result = self._execute("sutra_045", {"query": query})
        if intent_result.get("status") == "success":
            intent = intent_result.get("outputs", {}).get("intent", "general")
            working_memory["intent"] = intent
            working_memory["context"]["intent"] = intent
        self._add_trace("intent", working_memory["intent"])
        
        # Step 4: Knowledge Retriever (sutra_074)
        knowledge_result = self._execute("sutra_074", {
            "query": query,
            "district": working_memory["context"].get("district", ""),
            "crop": ""
        })
        if knowledge_result.get("status") == "success":
            working_memory["knowledge"] = knowledge_result.get("outputs", {}).get("knowledge_results", [])
        self._add_trace("knowledge", len(working_memory["knowledge"]))
        
        # Step 5: Retrieval Ranker (sutra_077)
        ranker_result = self._execute("sutra_077", {
            "query": query,
            "knowledge_results": working_memory["knowledge"]
        })
        if ranker_result.get("status") == "success":
            working_memory["ranked_knowledge"] = ranker_result.get("outputs", {}).get("ranked_results", [])
        self._add_trace("ranked", len(working_memory["ranked_knowledge"]))
        
        # Step 6: Clarification Check (sutra_078)
        clar_result = self._execute("sutra_078", {
            "query": query,
            "intent": working_memory["intent"],
            "working_memory": working_memory
        })
        if clar_result.get("status") == "success":
            needs_clar = clar_result.get("outputs", {}).get("needs_clarification", False)
            if needs_clar:
                working_memory["clarification_needed"] = True
                working_memory["clarification_questions"] = clar_result.get("outputs", {}).get("questions", [])
                self._add_trace("clarification", working_memory["clarification_questions"])
        
        # Step 7: If clarification needed, return questions
        if working_memory["clarification_needed"]:
            return {
                "status": "needs_clarification",
                "questions": working_memory["clarification_questions"],
                "query": query,
                "intent": working_memory["intent"],
                "trace": self.trace,
                "elapsed_ms": round((time.time() - start_time) * 1000, 1)
            }
        
        # Step 8: Query Planner (sutra_069)
        planner_result = self._execute("sutra_069", {
            "query": query,
            "intent": working_memory["intent"]
        })
        sequence = planner_result.get("outputs", {}).get("sequence", ["sutra_041"])
        self._add_trace("planner", sequence[:3])
        
        # Step 9: Execute domain sutras with context
        results = {}
        for sutra_id in sequence:
            if sutra_id in ["sutra_068", "sutra_069", "sutra_070", "sutra_071", "sutra_072",
                           "sutra_073", "sutra_074", "sutra_075", "sutra_076", "sutra_077",
                           "sutra_078", "sutra_079"]:
                continue
            
            inputs = {
                "query": query,
                "location": working_memory["context"].get("location", ""),
                "district": working_memory["context"].get("district", ""),
                "season": working_memory["context"].get("season", ""),
                "soil_type": working_memory["profile"].get("soil_type", ""),
                "crop_history": working_memory["profile"].get("crop_history", [])
            }
            
            result = self._execute(sutra_id, inputs)
            if result.get("status") == "success":
                outputs = result.get("outputs", {})
                results[sutra_id] = outputs
                # Deduplicate merging
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
        
        # Step 10: Multi-Hop Reasoner with ranked knowledge
        reasoner_result = self._execute("sutra_070", {
            "results": results,
            "query": query,
            "context": working_memory["context"],
            "ranked_knowledge": working_memory["ranked_knowledge"]
        })
        if reasoner_result.get("status") == "success":
            working_memory["synthesis"] = reasoner_result.get("outputs", {}).get("synthesis", "")
            working_memory["sources"] = reasoner_result.get("outputs", {}).get("sources", [])
        self._add_trace("reasoner", working_memory["synthesis"][:50])
        
        # Step 11: Evidence Quality Scorer (sutra_079)
        quality_result = self._execute("sutra_079", {
            "answer": working_memory["synthesis"],
            "sources": working_memory["sources"],
            "ranked_results": working_memory["ranked_knowledge"],
            "domain": working_memory["intent"]
        })
        if quality_result.get("status") == "success":
            working_memory["confidence"] = quality_result.get("outputs", {}).get("quality_score", 0.5)
            working_memory["evidence"] = quality_result.get("outputs", {})
        self._add_trace("quality", working_memory["confidence"])
        
        # Step 12: Response Validator (sutra_072)
        validator_result = self._execute("sutra_072", {
            "response": working_memory["synthesis"],
            "confidence": working_memory["confidence"],
            "sources": working_memory["sources"]
        })
        if validator_result.get("status") == "success":
            working_memory["approved"] = validator_result.get("outputs", {}).get("approved", False)
        self._add_trace("validator", working_memory["approved"])
        
        elapsed = time.time() - start_time
        
        return {
            "status": "success",
            "query": query,
            "intent": working_memory["intent"],
            "answer": working_memory["synthesis"],
            "confidence": working_memory["confidence"],
            "approved": working_memory["approved"],
            "sources": working_memory["sources"],
            "profile": working_memory["profile"],
            "context": working_memory["context"],
            "evidence": working_memory["evidence"],
            "ranked_knowledge": working_memory["ranked_knowledge"][:3],
            "trace": self.trace,
            "elapsed_ms": round(elapsed * 1000, 1)
        }
    
    def _extract_location(self, query: str) -> str:
        """Extract location from query."""
        query_lower = query.lower()
        districts = [
            "bongaigaon", "barpeta", "jorhat", "nagaon", "dibrugarh",
            "sonitpur", "dhubri", "goalpara", "kokrajhar", "tinsukia",
            "sivasagar", "golaghat", "lakhimpur", "dhemaji", "morigaon",
            "nalbari", "kamrup", "cachar", "hailakandi", "karimganj",
            "karbi_anglong", "dima_hasao", "chirang", "udalguri", "baksa"
        ]
        for district in districts:
            if district in query_lower:
                return district
        if "assam" in query_lower or "axom" in query_lower:
            return "assam"
        return ""
    
    def _extract_season(self, query: str) -> str:
        """Extract season from query."""
        query_lower = query.lower()
        seasons = ["kharif", "rabi", "summer", "winter", "monsoon"]
        for season in seasons:
            if season in query_lower:
                return season
        return ""
    
    def _execute(self, sutra_id: str, inputs: dict) -> dict:
        """Execute a single sutra with error handling."""
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
        """Add a trace entry."""
        if isinstance(value, list):
            value = str(value[:3]) if len(value) > 3 else str(value)
        self.trace.append({"step": step, "value": str(value)[:50]})
    
    def explain(self, query: str) -> str:
        """Generate an explanation of the pipeline."""
        result = self.process(query)
        
        if result.get("status") == "needs_clarification":
            lines = [
                "=" * 50,
                f"📝 Query: {query}",
                "=" * 50,
                "❓ Clarification Needed:",
            ]
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
            f"⏱️ Time: {result['elapsed_ms']:.1f}ms",
            "",
            "📋 Pipeline Trace:"
        ]
        
        for step in self.trace:
            lines.append(f"  ├── {step['step']}: {step['value']}")
        
        lines.append("")
        lines.append("📊 Profile:")
        for k, v in result.get('profile', {}).items():
            if v not in [None, "", [], {}]:
                lines.append(f"  ├── {k}: {v}")
        
        lines.append("")
        lines.append("📊 Context:")
        for k, v in result.get('context', {}).items():
            if v not in [None, "", []]:
                lines.append(f"  ├── {k}: {v}")
        
        lines.append("")
        lines.append("📊 Answer:")
        lines.append(f"  {result['answer'][:300]}")
        if len(result['answer']) > 300:
            lines.append("  ...")
        lines.append("=" * 50)
        
        return "\n".join(lines)
