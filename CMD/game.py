import random

# Store the current state of the game
game_state = {"active_game": None}

def execute(user_message):
    # User wants to quit the game
    if user_message.strip().lower() == "quit":
        game_state["active_game"] = None
        return "Thanks for playing! To start again, choose a game number (1-5)."

    # If no active game, list games to choose
    if game_state["active_game"] is None:
        games = [
            "Guess the Number",
            "Rock, Paper, Scissors",
            "Word Scramble",
            "Math Quiz",
            "Trivia"
        ]
        if user_message.strip().isdigit():
            choice = int(user_message.strip())
            if 1 <= choice <= 5:
                game_state["active_game"] = choice
                return start_game(choice)
            else:
                return "Invalid choice! Please reply with a number between 1 and 5."
        else:
            game_list = "\n".join([f"{i + 1}. {game}" for i, game in enumerate(games)])
            return f"Here are 5 games you can play:\n{game_list}\n\nReply with the number of the game you want to play (1-5)."
    else:
        # Continue with the active game
        return continue_game(game_state["active_game"], user_message)


def start_game(choice):
    if choice == 1:
        return "Welcome to 'Guess the Number'! I picked a number between 1 and 10. Guess it!"
    elif choice == 2:
        return "Welcome to 'Rock, Paper, Scissors'! Reply with Rock, Paper, or Scissors."
    elif choice == 3:
        return "Welcome to 'Word Scramble'! Unscramble this word: " + play_word_scramble()
    elif choice == 4:
        return play_math_quiz()
    elif choice == 5:
        return play_trivia()


def continue_game(choice, user_message):
    if choice == 1:
        return play_guess_number(user_message)
    elif choice == 2:
        return play_rock_paper_scissors(user_message)
    elif choice == 3:
        return check_word_scramble(user_message)
    elif choice == 4:
        return check_math_quiz(user_message)
    elif choice == 5:
        return check_trivia(user_message)


# Game 1: Guess the Number
secret_number = random.randint(1, 10)

def play_guess_number(user_message):
    global secret_number
    if user_message.strip().isdigit():
        guess = int(user_message.strip())
        if guess == secret_number:
            secret_number = random.randint(1, 10)  # Reset for replay
            return "Correct! I picked another number. Guess it again or type 'quit' to exit."
        else:
            return "Wrong guess! Try again or type 'quit' to exit."
    else:
        return "Invalid input! Please guess a number between 1 and 10 or type 'quit'."


# Game 2: Rock, Paper, Scissors
def play_rock_paper_scissors(user_message):
    options = ["rock", "paper", "scissors"]
    bot_choice = random.choice(options)
    user_choice = user_message.strip().lower()

    if user_choice in options:
        if user_choice == bot_choice:
            return f"It's a tie! I also chose {bot_choice}. Play again or type 'quit'."
        elif (user_choice == "rock" and bot_choice == "scissors") or \
             (user_choice == "scissors" and bot_choice == "paper") or \
             (user_choice == "paper" and bot_choice == "rock"):
            return f"You win! I chose {bot_choice}. Play again or type 'quit'."
        else:
            return f"You lose! I chose {bot_choice}. Play again or type 'quit'."
    else:
        return "Invalid choice! Please reply with Rock, Paper, or Scissors, or type 'quit'."


# Game 3: Word Scramble
words = ["python", "developer", "keyboard", "program", "challenge"]
scrambled_word = ""
original_word = ""

def play_word_scramble():
    global scrambled_word, original_word
    original_word = random.choice(words)
    scrambled_word = "".join(random.sample(original_word, len(original_word)))
    return scrambled_word

def check_word_scramble(user_message):
    global original_word
    if user_message.strip().lower() == original_word:
        return f"Correct! The word was '{original_word}'. Try another or type 'quit'.\nUnscramble: {play_word_scramble()}"
    else:
        return f"Wrong! Try again or type 'quit'. Unscramble: {scrambled_word}"


# Game 4: Math Quiz
math_answer = 0

def play_math_quiz():
    global math_answer
    a = random.randint(1, 10)
    b = random.randint(1, 10)
    math_answer = a + b
    return f"What's {a} + {b}? Reply with your answer or type 'quit'."

def check_math_quiz(user_message):
    global math_answer
    if user_message.strip().isdigit() and int(user_message.strip()) == math_answer:
        return f"Correct! Try another:\n{play_math_quiz()}"
    else:
        return "Wrong answer! Try again or type 'quit'."


# Game 5: Trivia
trivia_question = ""
trivia_answer = ""

def play_trivia():
    global trivia_question, trivia_answer
    trivia_questions = [
        ("What is the capital of France?", "Paris"),
        ("Who wrote 'To Kill a Mockingbird'?", "Harper Lee"),
        ("What is the square root of 64?", "8"),
        ("Who painted the Mona Lisa?", "Leonardo da Vinci"),
        ("What is the largest planet in our solar system?", "Jupiter"),
    ]
    trivia_question, trivia_answer = random.choice(trivia_questions)
    return f"Trivia Time! {trivia_question} (Reply with your answer or type 'quit'.)"

def check_trivia(user_message):
    global trivia_answer
    if user_message.strip().lower() == trivia_answer.lower():
        return f"Correct! Try another:\n{play_trivia()}"
    else:
        return "Wrong answer! Try again or type 'quit'."
