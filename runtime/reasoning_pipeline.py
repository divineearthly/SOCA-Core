"""
SOCA Reasoning Pipeline
Orchestrates the full reasoning flow from query to answer
"""

import sys
import time
sys.path.append('runtime')
from soca_runtime import SOCARuntime

class ReasoningPipeline:
    def __init__(self):
        self.runtime = SOCARuntime()
        self.trace = []
    
    def process(self, query: str, user_id: str = "anonymous") -> dict:
        """Process a query through the full reasoning pipeline."""
        start_time = time.time()
        self.trace = []
        
        # Step 1: Intent Classification (sutra_045)
        intent_result = self._execute("sutra_045", {"query": query})
        intent = intent_result.get("outputs", {}).get("intent", "general")
        intent_conf = intent_result.get("confidence", 0.5)
        self.trace.append({"step": "intent", "result": intent, "confidence": intent_conf})
        
        # Step 2: Context Builder (sutra_068)
        context_result = self._execute("sutra_068", {
            "query": query,
            "user_id": user_id,
            "language": "en"
        })
        context = context_result.get("outputs", {})
        self.trace.append({"step": "context", "result": context})
        
        # Step 3: Query Planner (sutra_069)
        planner_result = self._execute("sutra_069", {
            "query": query,
            "intent": intent
        })
        sequence = planner_result.get("outputs", {}).get("sequence", ["sutra_041"])
        self.trace.append({"step": "planner", "sequence": sequence})
        
        # Step 4: Execute each sutra in sequence
        results = {}
        for sutra_id in sequence:
            if sutra_id not in ["sutra_068", "sutra_069", "sutra_070", "sutra_071", "sutra_072"]:
                result = self._execute(sutra_id, {"query": query})
                if result.get("status") == "success":
                    results[sutra_id] = result.get("outputs", {})
        
        # Step 5: Multi-Hop Reasoner (sutra_070)
        reasoner_result = self._execute("sutra_070", {
            "results": results,
            "query": query
        })
        synthesis = reasoner_result.get("outputs", {}).get("synthesis", "")
        self.trace.append({"step": "reasoner", "synthesis": synthesis[:100]})
        
        # Step 6: Fact Checker (sutra_071)
        fact_result = self._execute("sutra_071", {
            "answer": synthesis,
            "sources": list(results.keys()),
            "domain": intent
        })
        verified = fact_result.get("outputs", {}).get("verified", False)
        confidence = fact_result.get("confidence", 0.5)
        self.trace.append({"step": "fact_check", "verified": verified, "confidence": confidence})
        
        # Step 7: Response Validator (sutra_072)
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
            "trace": self.trace,
            "elapsed_ms": round(elapsed * 1000, 1)
        }
    
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
        """Generate an explanation of the pipeline for a query."""
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
            "📋 Pipeline Trace:"
        ]
        
        for step in result.get('trace', []):
            step_name = step.get('step', 'unknown')
            details = []
            for key, value in step.items():
                if key not in ['step']:
                    if isinstance(value, dict):
                        details.append(f"{key}={str(list(value.keys()))[:30]}")
                    else:
                        details.append(f"{key}={str(value)[:30]}")
            lines.append(f"  ├── {step_name}: {', '.join(details)}")
        
        lines.append("")
        lines.append("📊 Answer:")
        lines.append(f"  {result['answer'][:200]}")
        if len(result['answer']) > 200:
            lines.append("  ...")
        lines.append("=" * 50)
        
        return "\n".join(lines)
