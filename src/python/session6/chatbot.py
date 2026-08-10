'''
our chatbot
'''
import random
responses = {
    "hello": ["Hello!", "Hi there!", "Greetings!"],
    "how are you": ["I'm doing well, thank you!", "I'm fine, how about you?"],
    "goodbye": ["Goodbye!", "See you later!", "Farewell!"],
    "default": ["I'm sorry, I didn't understand.", "Could you please rephrase that?"]
}
 
def get_response(user_input):
    for key in responses:
        if key in user_input:
            return random.choice(responses[key])
    return random.choice(responses["default"])
 

 