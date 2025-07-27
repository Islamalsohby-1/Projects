def get_country_profiles():
    """Return country profiles with goals, stance, and constraints."""
    return {
        "USA": {
            "stance": "Liberal, innovation-driven",
            "goals": "Lead in AI innovation, protect national security",
            "constraints": "High GDP, limited regulation appetite"
        },
        "China": {
            "stance": "Aggressive, state-controlled",
            "goals": "Global AI dominance, strict data control",
            "constraints": "High tech dev, authoritarian oversight"
        },
        "EU": {
            "stance": "Diplomatic, ethics-focused",
            "goals": "Enforce strict AI ethics, protect privacy",
            "constraints": "Complex regulatory framework"
        },
        "India": {
            "stance": "Balanced, development-focused",
            "goals": "Leverage AI for economic growth, affordable solutions",
            "constraints": "Emerging tech ecosystem, resource limits"
        }
    }