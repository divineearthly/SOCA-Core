"""
SOCA Agentic Pipeline - Shared Working Memory Architecture
"""

import sys
import time
import re
sys.path.append('runtime')
from soca_runtime import SOCARuntime

class AgenticPipeline:
    def __init__(self):
        self.runtime = SOCARuntime()
        self.trace = []
    
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
            "evidence": [],
            "results": {},
            "synthesis": "",
            "confidence": 0.5,
            "approved": False,
            "sources": [],
            "trace": []
        }
        
        # STEP 1: Extract location and season from query
        location = self._extract_location(query)
        if location:
            working_memory["context"]["location"] = location
            working_memory["context"]["district"] = location
        
        season = self._extract_season(query)
        if season:
            working_memory["context"]["season"] = season
        
        # STEP 2: Intent Classification (sutra_045)
        intent_result = self._execute("sutra_045", {"query": query})
        if intent_result.get("status") == "success":
            intent = intent_result.get("outputs", {}).get("intent", "general")
            working_memory["intent"] = intent
            working_memory["context"]["intent"] = intent
        self._add_trace("intent", working_memory["intent"])
        
        # STEP 3: Profile Context Injector (sutra_073)
        profile_result = self._execute("sutra_073", {
            "user_id": user_id,
            "query": query,
            "working_memory": working_memory
        })
        if profile_result.get("status") == "success":
            profile = profile_result.get("outputs", {}).get("working_memory", {}).get("profile", {})
            working_memory["profile"] = profile
            # Override location with profile district if available
            if profile.get("district") and profile["district"] != "bongaigaon":
                working_memory["context"]["district"] = profile["district"]
        self._add_trace("profile", working_memory["profile"].get("district", "none"))
        
        # STEP 4: Knowledge Retriever (sutra_074)
        knowledge_result = self._execute("sutra_074", {
            "query": query,
            "district": working_memory["context"].get("district", ""),
            "crop": ""
        })
        if knowledge_result.get("status") == "success":
            working_memory["knowledge"] = knowledge_result.get("outputs", {}).get("knowledge_results", [])
        self._add_trace("knowledge", len(working_memory["knowledge"]))
        
        # STEP 5: Query Planner (sutra_069)
        planner_result = self._execute("sutra_069", {
            "query": query,
            "intent": working_memory["intent"]
        })
        sequence = planner_result.get("outputs", {}).get("sequence", ["sutra_041"])
        self._add_trace("planner", sequence)
        
        # STEP 6: Execute domain sutras
        results = {}
        for sutra_id in sequence:
            if sutra_id in ["sutra_068", "sutra_069", "sutra_070", "sutra_071", "sutra_072", 
                           "sutra_073", "sutra_074", "sutra_075"]:
                continue
            
            # Build inputs from working memory
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
                # Merge safely
                for k, v in outputs.items():
                    if v not in [None, "", []]:
                        if k not in working_memory["results"]:
                            working_memory["results"][k] = []
                        if isinstance(v, list):
                            working_memory["results"][k].extend(v)
                        else:
                            working_memory["results"][k].append(v)
        
        self._add_trace("domain", len(results))
        
        # STEP 7: Multi-Hop Reasoner (sutra_070)
        reasoner_result = self._execute("sutra_070", {
            "results": results,
            "query": query,
            "context": working_memory["context"]
        })
        if reasoner_result.get("status") == "success":
            working_memory["synthesis"] = reasoner_result.get("outputs", {}).get("synthesis", "")
            working_memory["sources"] = reasoner_result.get("outputs", {}).get("sources", [])
        self._add_trace("reasoner", working_memory["synthesis"][:50])
        
        # STEP 8: Evidence Aggregator (sutra_075)
        evidence_result = self._execute("sutra_075", {
            "answer": working_memory["synthesis"],
            "sources": working_memory["sources"],
            "knowledge_results": working_memory["knowledge"],
            "domain": working_memory["intent"]
        })
        if evidence_result.get("status") == "success":
            working_memory["confidence"] = evidence_result.get("outputs", {}).get("confidence", 0.5)
            working_memory["evidence"] = evidence_result.get("outputs", {})
        self._add_trace("evidence", working_memory["confidence"])
        
        # STEP 9: Response Validator (sutra_072)
        validator_result = self._execute("sutra_072", {
            "response": working_memory["synthesis"],
            "confidence": working_memory["confidence"],
            "sources": working_memory["sources"]
        })
        if validator_result.get("status") == "success":
            working_memory["approved"] = validator_result.get("outputs", {}).get("approved", False)
            working_memory["quality"] = validator_result.get("outputs", {}).get("quality", 0)
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
        self.trace.append({"step": step, "value": str(value)[:50]})
    
    def explain(self, query: str) -> str:
        """Generate an explanation of the pipeline."""
        result = self.process(query)
        
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
            if v not in [None, "", []]:
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
