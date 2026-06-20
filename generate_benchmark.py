"""Generate 100 benchmark queries across domains"""
import json
import random

queries = []

# Agriculture queries
agriculture = [
    ("What crop should I grow in Assam?", ["sutra_021", "sutra_025"]),
    ("Best crop for loamy soil", ["sutra_021"]),
    ("What to plant in kharif season?", ["sutra_021", "sutra_025"]),
    ("How to control pests on rice?", ["sutra_026"]),
    ("What is the best irrigation method?", ["sutra_027"]),
    ("Which crop needs less water?", ["sutra_027", "sutra_021"]),
    ("What to grow in clay soil?", ["sutra_021"]),
    ("Pest management for cotton", ["sutra_026"]),
    ("Farming advice for monsoon season", ["sutra_025"]),
    ("How to prevent crop diseases?", ["sutra_026"])
]
for q, s in agriculture:
    queries.append({"query": q, "expected": s, "domain": "agriculture"})

# Education queries
education = [
    ("What is addition?", ["sutra_022"]),
    ("Explain multiplication", ["sutra_022"]),
    ("How to subtract numbers?", ["sutra_022"]),
    ("What is division?", ["sutra_022"]),
    ("Explain fractions", ["sutra_022"]),
    ("What are decimals?", ["sutra_022"]),
    ("Math tutor for addition", ["sutra_022"]),
    ("How to learn multiplication?", ["sutra_022"]),
    ("Explain subtraction to kids", ["sutra_022"]),
    ("What is the sum of numbers?", ["sutra_022"])
]
for q, s in education:
    queries.append({"query": q, "expected": s, "domain": "education"})

# Translation queries
translation = [
    ("Translate hello to Hindi", ["sutra_024"]),
    ("How to say water in Assamese?", ["sutra_024"]),
    ("Translate food to Bengali", ["sutra_024"]),
    ("What is earth in Sanskrit?", ["sutra_024"]),
    ("Translate sky to Hindi", ["sutra_024"]),
    ("Friend in Bengali", ["sutra_024"]),
    ("Assamese translation for water", ["sutra_024"]),
    ("Sanskrit word for earth", ["sutra_024"]),
    ("Hindi translation of hello", ["sutra_024"]),
    ("Translate friend to Assamese", ["sutra_024"])
]
for q, s in translation:
    queries.append({"query": q, "expected": s, "domain": "translation"})

# Medicinal plants queries
medicinal = [
    ("What is tulsi used for?", ["sutra_023"]),
    ("Benefits of neem", ["sutra_023"]),
    ("How to use aloe vera?", ["sutra_023"]),
    ("What is ginger good for?", ["sutra_023"]),
    ("Turmeric health benefits", ["sutra_023"]),
    ("Amla uses", ["sutra_023"]),
    ("Medicinal uses of tulsi", ["sutra_023"]),
    ("Neem for skin", ["sutra_023"]),
    ("Aloe vera for burns", ["sutra_023"]),
    ("Ginger for digestion", ["sutra_023"])
]
for q, s in medicinal:
    queries.append({"query": q, "expected": s, "domain": "medicinal"})

# Mixed queries
mixed = [
    ("What crop and how to manage water?", ["sutra_021", "sutra_027"]),
    ("Pest control and crop selection", ["sutra_026", "sutra_021"]),
    ("Seasonal farming in Assam", ["sutra_025", "sutra_021"]),
    ("Math and translation help", ["sutra_022", "sutra_024"]),
    ("Medicinal plant and farming", ["sutra_023", "sutra_021"])
]
for q, s in mixed:
    queries.append({"query": q, "expected": s, "domain": "mixed"})

# Save
with open('benchmark_queries.json', 'w') as f:
    json.dump(queries, f, indent=2)

print(f"✅ Generated {len(queries)} benchmark queries")
