"""Test the reasoning pipeline"""
import sys
sys.path.append('.')
from runtime.soca_runtime import SOCARuntime

def test_reasoning():
    runtime = SOCARuntime()
    
    queries = [
        "What crop should I grow?",
        "What crop should I grow in Bongaigaon?",
        "What crop should I grow in Bongaigaon during kharif?"
    ]
    
    print("🧠 Testing Reasoning Pipeline")
    print("=" * 50)
    
    for query in queries:
        print(f"\n📝 Query: {query}")
        
        # Step 1: Classify intent
        intent_result = runtime.solve_sequence(['sutra_045'], {'query': query})
        if 'outputs' in intent_result:
            intent = intent_result['outputs'].get('intent', 'general')
            confidence = intent_result['outputs'].get('confidence', 0)
            print(f"  Intent: {intent} ({confidence})")
        else:
            print(f"  Intent failed: {intent_result.get('error', 'Unknown')}")
            continue
        
        # Step 2: Check for clarification
        clar_result = runtime.solve_sequence(['sutra_046'], {
            'query': query,
            'intent': intent
        })
        if 'outputs' in clar_result:
            missing = clar_result['outputs'].get('missing', [])
            follow_up = clar_result['outputs'].get('follow_up', [])
            
            if missing:
                print(f"  Missing: {missing}")
                for q in follow_up:
                    print(f"  → {q}")
            else:
                print("  ✅ All information provided")
        else:
            print(f"  Clarification failed: {clar_result.get('error', 'Unknown')}")
            
        print("-" * 30)

if __name__ == "__main__":
    test_reasoning()
