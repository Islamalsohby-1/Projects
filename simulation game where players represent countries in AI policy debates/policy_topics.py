def get_topic_details(topic):
    """Return details and template for a policy topic."""
    topics = {
        "AI Surveillance Laws": {
            "description": "Debate regulations on AI-powered surveillance technologies.",
            "template": "Global treaty to limit AI surveillance to protect privacy while ensuring security."
        },
        "Military AI Limits": {
            "description": "Set boundaries on autonomous AI in military applications.",
            "template": "Agreement to ban fully autonomous lethal AI weapons."
        },
        "Global AI Ethics": {
            "description": "Establish universal AI ethics and fairness principles.",
            "template": "Framework for ethical AI development, inspired by EU AI Act."
        },
        "Data Sharing": {
            "description": "Negotiate cross-border AI data sharing policies.",
            "template": "Protocol for secure, transparent AI data sharing between nations."
        },
        "Model Regulation": {
            "description": "Regulate large AI models and alignment research.",
            "template": "Global standards for transparency in large-scale AI model development."
        }
    }
    return topics.get(topic, {"description": "General AI policy debate", "template": "Draft a global AI policy."})