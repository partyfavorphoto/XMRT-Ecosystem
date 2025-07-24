"""
A minimal Eliza-style chatbot backend for XMRT-Ecosystem.
"""

import re

class ElizaBot:
    def __init__(self):
        self.patterns = [
            (r'I need (.*)', 'Why do you need {0}?'),
            (r'Why don'?t you ([^\?]*)\??', 'Do you really think I don't {0}?'),
            (r'Why can'?t I ([^\?]*)\??', 'What makes you think you can't {0}?'),
            (r'I can'?t (.*)', 'How do you know you can't {0}?'),
            (r'I am (.*)', 'How long have you been {0}?'),
            (r'I'?m (.*)', 'How does being {0} make you feel?'),
            (r'How (.*)', 'How do you suppose?'),
            (r'Because (.*)', 'Is that the real reason?'),
            (r'(.*) sorry (.*)', 'No need to apologize.'),
            (r'Hello(.*)', 'Hello! How can I help you today?'),
            (r'Hi(.*)', 'Hi there! What brings you here?'),
            (r'(.*)', 'Tell me more about that.')
        ]

    def respond(self, text):
        for pattern, response in self.patterns:
            match = re.match(pattern, text, re.IGNORECASE)
            if match:
                groups = match.groups()
                return response.format(*groups) if groups else response
        return "Can you elaborate?"

if __name__ == "__main__":
    bot = ElizaBot()
    print("Welcome to Eliza! (Type 'quit' to exit)")
    while True:
        user_input = input("You: ")
        if user_input.strip().lower() == "quit":
            print("Eliza: Goodbye!")
            break
        print("Eliza:", bot.respond(user_input))
