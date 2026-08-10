from chatbot import get_response
def main():
    print("chatbot : hi how i can help you!")
    while True:
        user_input = input("User:  ").lower()
        response = get_response(user_input)
        print("chatbot ", response)
       
        if user_input == "goodbye":
            break
 