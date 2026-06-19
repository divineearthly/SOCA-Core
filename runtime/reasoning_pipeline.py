"""
SOCA Reasoning Pipeline - With Shared Working Memory
"""

import sys
import time
import re
sys.path.append('runtime')
from soca_runtime import SOCARuntime

class ReasoningPipeline:
    def __init__(self):
        self.runtime = SOCARuntime()
        self.trace = []
    
    def process(self, query: str, user_id: str = "anonymous") -> dict:
        start_time = time.time()
        self.trace = []
        
        # Initialize working memory
        working_memory = {
            "query": query,
            "user_id": user_id,
            "language": "en"
        }
        
        # Step 1: Extract location from query
        location = self._extract_location(query)
        if location:
            working_memory["location"] = location
            working_memory["district"] = location
        
        # Step 2: Extract season from query
        season = self._extract_season(query)
        if season:
            working_memory["season"] = season
        
        # Step 3: Intent Classification (sutra_045)
        intent_result = self._execute("sutra_045", {"query": query})
        intent = intent_result.get("outputs", {}).get("intent", "general")
        working_memory["intent"] = intent
        self.trace.append({"step": "intent", "result": intent})
        
        # Step 4: Context Builder (sutra_068)
        context_result = self._execute("sutra_068", working_memory)
        if context_result.get("status") == "success":
            working_memory.update(context_result.get("outputs", {}))
        self.trace.append({"step": "context", "memory": list(working_memory.keys())})
        
        # Step 5: Query Planner (sutra_069)
        planner_result = self._execute("sutra_069", {
            "query": query,
            "intent": intent
        })
        sequence = planner_result.get("outputs", {}).get("sequence", ["sutra_041"])
        self.trace.append({"step": "planner", "sequence": sequence})
        
        # Step 6: Execute each sutra with shared working memory
        results = {}
        for sutra_id in sequence:
            # Skip pipeline sutras
            if sutra_id in ["sutra_068", "sutra_069", "sutra_070", "sutra_071", "sutra_072"]:
                continue
            
            # Pass working memory to each sutra
            result = self._execute(sutra_id, working_memory)
            if result.get("status") == "success":
                outputs = result.get("outputs", {})
                results[sutra_id] = outputs
                # Update working memory with outputs
                working_memory.update(outputs)
        
        # Step 7: Multi-Hop Reasoner (sutra_070)
        reasoner_result = self._execute("sutra_070", {
            "results": results,
            "query": query,
            "context": working_memory
        })
        synthesis = reasoner_result.get("outputs", {}).get("synthesis", "")
        self.trace.append({"step": "reasoner", "synthesis": synthesis[:100]})
        
        # Step 8: Fact Checker (sutra_071)
        fact_result = self._execute("sutra_071", {
            "answer": synthesis,
            "sources": list(results.keys()),
            "domain": intent
        })
        verified = fact_result.get("outputs", {}).get("verified", False)
        confidence = fact_result.get("confidence", 0.5)
        self.trace.append({"step": "fact_check", "verified": verified, "confidence": confidence})
        
        # Step 9: Response Validator (sutra_072)
        validator_result = self._execute("sutra_072", {
            "response": synthesis,
            "confidence": confidence,
            "sources": list(results.keys())
        })
        approved = validator_result.get("outputs", {}).get("approved", False)
        quality = validator_result.get("outputs", {}).get("quality", 0)
        self.trace.append({"step": "validator", "approved": approved, "quality": quality})
        
        elapsed = time.time() - start_time
        
        return {
            "status": "success",
            "query": query,
            "intent": intent,
            "answer": synthesis,
            "verified": verified,
            "approved": approved,
            "confidence": confidence,
            "quality": quality,
            "sources": list(results.keys()),
            "working_memory": {k: v for k, v in working_memory.items() if k not in ["query", "user_id"]},
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
        
        # Check for state
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
    
    def explain(self, query: str) -> str:
        """Generate an explanation of the pipeline."""
        result = self.process(query)
        
        lines = [
            "=" * 50,
            f"📝 Query: {query}",
            "=" * 50,
            f"🎯 Intent: {result['intent']}",
            f"📊 Confidence: {result['confidence']:.2f}",
            f"✅ Verified: {result['verified']}",
            f"🏷️ Approved: {result['approved']}",
            f"⏱️ Time: {result['elapsed_ms']:.1f}ms",
            "",
            "📋 Working Memory:"
        ]
        
        for key, value in result.get('working_memory', {}).items():
            if key not in ['query', 'user_id']:
                lines.append(f"  ├── {key}: {str(value)[:50]}")
        
        lines.append("")
        lines.append("📊 Answer:")
        lines.append(f"  {result['answer'][:300]}")
        if len(result['answer']) > 300:
            lines.append("  ...")
        lines.append("=" * 50)
        
        return "\n".join(lines)
