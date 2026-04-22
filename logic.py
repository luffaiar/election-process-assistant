from nlp import get_nlp_response

def get_response(user_input):
    try:
        return get_nlp_response(user_input)
    except:
        return "Sorry, I couldn't understand. Try asking about voting or registration."
