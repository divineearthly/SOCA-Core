import json
import os

# Create assam_agriculture pack
assam_agri = {
    "name": "Assam Agriculture",
    "crops": [
        {"name": "Rice", "varieties": ["Sali", "Boro", "Ahu"]},
        {"name": "Tea", "varieties": ["CTC", "Orthodox"]},
        {"name": "Jute", "varieties": ["White", "Tossa"]},
        {"name": "Mustard", "varieties": ["Yellow", "Brown"]}
    ],
    "districts": [
        "Bongaigaon", "Barpeta", "Jorhat", "Dibrugarh", 
        "Nagaon", "Sonitpur", "Dhubri", "Goalpara"
    ]
}

# Create medicinal plants pack
medicinal = {
    "name": "Assam Medicinal Plants",
    "plants": [
        {"name": "Tulsi", "uses": ["Cough", "Cold"]},
        {"name": "Neem", "uses": ["Skin", "Dental"]},
        {"name": "Ginger", "uses": ["Digestion", "Nausea"]},
        {"name": "Turmeric", "uses": ["Anti-inflammatory"]},
        {"name": "Amla", "uses": ["Immunity", "Digestion"]}
    ]
}

# Save packs
os.makedirs("data/packs", exist_ok=True)

with open("data/packs/assam_agriculture.pack", "w") as f:
    json.dump(assam_agri, f, indent=2)

with open("data/packs/assam_medicinal.pack", "w") as f:
    json.dump(medicinal, f, indent=2)

print("✅ Created knowledge packs")
