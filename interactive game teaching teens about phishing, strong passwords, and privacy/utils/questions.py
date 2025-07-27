def get_phishing_questions():
    """Return a list of phishing challenge questions."""
    return [
        {
            "text": "Subject: Urgent Account Verification\nDear User, your account will be suspended unless you verify your details at [link].\nFrom: support@bank.com",
            "is_phishing": True,
            "image": "phishing_email1.jpg",
            "explanation": "Suspicious link and urgent tone are common phishing tactics."
        },
        {
            "text": "Subject: Meeting Reminder\nHi, don't forget our team meeting tomorrow at 10 AM.\nFrom: manager@company.com",
            "is_phishing": False,
            "image": None,
            "explanation": "Legitimate emails from known contacts are usually safe."
        },
        {
            "text": "Subject: You Won a Prize!\nClick here to claim your $1000 gift card!\nFrom: rewards@win.com",
            "is_phishing": True,
            "image": "phishing_email2.jpg",
            "explanation": "Unsolicited prize offers are a red flag for phishing."
        }
    ]

def get_privacy_questions():
    """Return a list of privacy quiz scenarios."""
    return [
        {
            "scenario": "You get a friend request on social media from someone you don't know. What should you do?",
            "options": ["Accept it", "Ignore it", "Share your profile link"],
            "correct_answer": "Ignore it",
            "explanation": "Unknown friend requests can lead to data harvesting."
        },
        {
            "scenario": "A website asks for your location. What’s the safest choice?",
            "options": ["Allow always", "Allow once", "Deny"],
            "correct_answer": "Deny",
            "explanation": "Denying location access protects your privacy unless necessary."
        },
        {
            "scenario": "You’re setting up a new app. It requests access to your contacts. What do you do?",
            "options": ["Grant access", "Skip", "Uninstall the app"],
            "correct_answer": "Skip",
            "explanation": "Avoid sharing contacts unless the app requires it for functionality."
        }
    ]