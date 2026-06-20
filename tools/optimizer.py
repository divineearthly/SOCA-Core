#!/usr/bin/env python3
"""
SOCA Optimization Tool
Analyzes telemetry and suggests improvements
"""

import sys
import os
import sqlite3
from datetime import datetime

def main():
    print("=" * 60)
    print("🕉️ SOCA SELF-OPTIMIZATION REPORT")
    print("=" * 60)
    print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    sys.path.append('runtime')
    from registry_manager import RegistryManager
    
    rm = RegistryManager()
    db_path = rm.db_path
    
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        
        # 1. Strategy Analysis
        print("\n📊 RETRIEVAL STRATEGY ANALYSIS")
        print("-" * 40)
        cursor.execute("""
            SELECT 
                retrieval_strategy,
                COUNT(*) as count,
                AVG(confidence) as avg_confidence,
                AVG(iterations) as avg_iterations
            FROM telemetry
            WHERE retrieval_strategy IS NOT NULL
            GROUP BY retrieval_strategy
            ORDER BY avg_confidence DESC
        """)
        rows = cursor.fetchall()
        
        if rows:
            print(f"{'Strategy':12} | {'Count':>6} | {'Confidence':>10} | {'Iterations':>10}")
            print("-" * 45)
            for r in rows:
                print(f"{r[0]:12} | {r[1]:>6} | {r[2]:>10.3f} | {r[3]:>10.1f}")
            
            # Recommendation
            best = rows[0]
            print(f"\n💡 Best Strategy: {best[0]} (confidence: {best[2]:.3f})")
        else:
            print("No strategy data yet")
        
        # 2. Repair Effectiveness
        print("\n🔧 REPAIR EFFECTIVENESS")
        print("-" * 40)
        cursor.execute("""
            SELECT 
                repair_type,
                COUNT(*) as total,
                SUM(CASE WHEN success THEN 1 ELSE 0 END) as successes,
                AVG(confidence_delta) as avg_delta
            FROM repair_history
            WHERE repair_type IS NOT NULL
            GROUP BY repair_type
            ORDER BY avg_delta DESC
        """)
        rows = cursor.fetchall()
        
        if rows:
            print(f"{'Repair Type':15} | {'Success':>8} | {'Delta':>10}")
            print("-" * 40)
            for r in rows:
                rate = f"{r[2]}/{r[1]} ({r[2]/r[1]*100:.1f}%)" if r[1] > 0 else "N/A"
                print(f"{r[0]:15} | {rate:>8} | {r[3]:>+10.3f}")
            
            best = rows[0]
            print(f"\n💡 Best Repair: {best[0]} (delta: {best[3]:+.3f})")
        else:
            print("No repair data yet")
        
        # 3. Intent Analysis
        print("\n🎯 INTENT ANALYSIS")
        print("-" * 40)
        cursor.execute("""
            SELECT 
                intent,
                COUNT(*) as count,
                AVG(confidence) as avg_confidence,
                AVG(iterations) as avg_iterations,
                SUM(CASE WHEN clarification_needed THEN 1 ELSE 0 END) as clarifications
            FROM telemetry
            GROUP BY intent
            ORDER BY count DESC
        """)
        rows = cursor.fetchall()
        
        if rows:
            print(f"{'Intent':15} | {'Count':>6} | {'Confidence':>10} | {'Clarify':>8}")
            print("-" * 50)
            for r in rows:
                print(f"{r[0] or 'unknown':15} | {r[1]:>6} | {r[2]:>10.3f} | {r[4]:>8}")
        else:
            print("No intent data yet")
        
        # 4. Optimization Suggestions
        print("\n💡 OPTIMIZATION SUGGESTIONS")
        print("-" * 40)
        
        suggestions = []
        
        # Check confidence
        cursor.execute("SELECT AVG(confidence) FROM telemetry")
        avg_conf = cursor.fetchone()[0] or 0
        
        if avg_conf < 0.6:
            suggestions.append("Consider lowering reflection threshold (current: 0.65)")
        elif avg_conf > 0.8:
            suggestions.append("Consider raising reflection threshold (current: 0.65)")
        else:
            suggestions.append(f"Confidence ({avg_conf:.3f}) is in a good range")
        
        # Check clarification rate
        cursor.execute("SELECT COUNT(*) FROM telemetry WHERE clarification_needed = 1")
        clar_count = cursor.fetchone()[0] or 0
        cursor.execute("SELECT COUNT(*) FROM telemetry")
        total = cursor.fetchone()[0] or 1
        clar_rate = clar_count / total
        
        if clar_rate > 0.3:
            suggestions.append(f"High clarification rate ({clar_rate:.1%}). Consider improving slot extraction.")
        else:
            suggestions.append(f"Clarification rate ({clar_rate:.1%}) is reasonable")
        
        # Check iteration count
        cursor.execute("SELECT AVG(iterations) FROM telemetry")
        avg_iter = cursor.fetchone()[0] or 0
        
        if avg_iter > 2:
            suggestions.append(f"High average iterations ({avg_iter:.1f}). Consider raising confidence threshold.")
        else:
            suggestions.append(f"Average iterations ({avg_iter:.1f}) is good")
        
        # Check query volume
        if total < 10:
            suggestions.append(f"Only {total} queries recorded. Run more queries for better insights.")
        
        # Check repair data
        cursor.execute("SELECT COUNT(*) FROM repair_history")
        repair_count = cursor.fetchone()[0] or 0
        if repair_count == 0:
            suggestions.append("No repair data recorded yet. Repairs will be tracked automatically.")
        
        for i, s in enumerate(suggestions, 1):
            print(f"  {i}. {s}")
        
        # 5. Summary
        print("\n📊 SUMMARY METRICS")
        print("-" * 40)
        print(f"  Total Queries:    {total}")
        print(f"  Average Confidence: {avg_conf:.3f}")
        print(f"  Average Iterations: {avg_iter:.1f}")
        print(f"  Clarification Rate: {clar_rate:.1%}")
        print(f"  Repair Records:   {repair_count}")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    main()
