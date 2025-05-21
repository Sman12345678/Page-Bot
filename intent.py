from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
train_data = [
    # generate_image intent
    ("generate image of a cat", "generate_image"),
    ("Create a picture or a dog", "generate_image"),
    ("create an ai image", "generate_image"),
    ("create an image of hyper realistic dog", "generate_image"),
    ("show me a picture of a mountain", "generate_image"),
    ("make a photo of a robot", "generate_image"),
    ("draw a dragon", "generate_image"),
    ("create an image of a unicorn", "generate_image"),
    ("I want a picture of a pizza", "generate_image"),
    ("give me a digital art of a fox", "generate_image"),
    ("please provide an illustration of a laptop", "generate_image"),
    ("generate a realistic photo of a lion", "generate_image"),
    ("make a painting of the night sky", "generate_image"),
    ("create digital art of outer space", "generate_image"),
    ("show a cartoon version of a penguin", "generate_image"),
    ("paint a fantasy landscape", "generate_image"),
    ("generate a drawing of a family at the beach", "generate_image"),
    ("draw a superhero", "generate_image"),
    ("generate an image of futuristic city", "generate_image"),
    ("show me a painting of New York City", "generate_image"),
    ("generate image of a cat", "generate_image"),
    ("imagine a cute dog", "generate_image"),
    ("imagine the picture of a young girl", "generate_image"),


    # general_chat intent
    ("how are you?", "general_chat"),
    ("Teach me how to code","general_chat"),
    ("Teach me how to draw","general_chat"),
    ("i want to know art and illustration ","general_chat"),
    ("Teach me painting, pictures ","general_chat"),
    ("what's the weather?", "general_chat"),
    ("tell me a joke", "general_chat"),
    ("who is the president?", "general_chat"),
    ("explain quantum physics", "general_chat"),
    ("what time is it?", "general_chat"),
    ("how do I cook rice?", "general_chat"),
    ("where is the nearest restaurant?", "general_chat"),
    ("what's the capital of France?", "general_chat"),
    ("can you help me with my homework?", "general_chat"),
    ("tell me the news", "general_chat"),
    ("what is the meaning of life?", "general_chat"),
    ("define artificial intelligence", "general_chat"),
    ("translate hello to Spanish", "general_chat"),
    ("what is 2 plus 2?", "general_chat"),
    ("how do I change a tire?", "general_chat"),
    ("recommend a movie", "general_chat"),
    ("who won the game last night?", "general_chat"),
    ("what's your name?", "general_chat"),
    ("how old are you?", "general_chat"),
    ("what do you think about technology?", "general_chat"),
    ("can you tell me a fun fact?", "general_chat"),
    ("what's your favorite color?", "general_chat"),
    ("how do I improve my memory?", "general_chat"),
    ("explain how rainbows are formed", "general_chat"),
    ("who invented the telephone?", "general_chat"),
    ("what's your favorite movie?", "general_chat"),
    ("how can I be more productive?", "general_chat"),
    ("what's the best way to learn Python?", "general_chat"),
    ("what is the tallest building in the world?", "general_chat"),
    ("how do airplanes fly?", "general_chat"),
    ("can you recommend a good book?", "general_chat"),
    ("tell me a riddle", "general_chat"),
    ("what's your favorite animal?", "general_chat"),
    ("how do you stay motivated?", "general_chat"),
    ("what is climate change?", "general_chat"),
    ("who painted the Mona Lisa?", "general_chat"),
    ("what is your purpose?", "general_chat"),
    ("how can I learn to play guitar?", "general_chat"),
    ("what is artificial intelligence used for?", "general_chat"),
    ("what's the largest ocean on Earth?", "general_chat"),
    ("what are black holes?", "general_chat"),
    ("why is the sky blue?", "general_chat"),
    ("how do I make pancakes?", "general_chat"),
    ("what is the speed of light?", "general_chat"),
    ("who wrote Harry Potter?", "general_chat"),
    ("what's the population of the world?", "general_chat"),
    ("can you explain photosynthesis?", "general_chat"),
    ("what is your favorite food?", "general_chat"),
]

class SmallIntentClassifier:
    def __init__(self):
        self.vectorizer = TfidfVectorizer()
        self.model = LogisticRegression()
        self._train()

    def _train(self):
        texts, intents = zip(*train_data)
        X = self.vectorizer.fit_transform(texts)
        self.model.fit(X, intents)

    def predict_intent(self, text):
        X = self.vectorizer.transform([text])
        return self.model.predict(X)[0]

classifier = SmallIntentClassifier()
