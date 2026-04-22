from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity

responses = {
    "how to register": "To register, visit the NVSP website, fill Form 6, and submit ID proof.",
    "how to vote": "Go to your polling booth, verify your ID, and cast your vote.",
    "election timeline": "Election stages include announcement, campaigning, voting, counting, and results.",
    "minimum age": "You must be at least 18 years old to vote.",
    "voter id": "You can use Voter ID, Aadhaar, Passport, or Driving License.",
    "first time voter": "Register early and carry valid ID to the polling booth."
}

questions = list(responses.keys())
vectorizer = CountVectorizer().fit_transform(questions)

def get_nlp_response(user_input):
    user_vec = CountVectorizer().fit(questions + [user_input]).transform([user_input])
    similarity = cosine_similarity(user_vec, vectorizer)
    index = similarity.argmax()

    return responses[questions[index]]
