import os
import pandas as pd
import random
from openai import OpenAI


# 1. SET UP YOUR API KEY
# Make sure your OPENAI_API_KEY is set as an environment variable.
# For example, in terminal: export OPENAI_API_KEY="sk-..."
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# 2. PATH TO YOUR CSV FILE
FLASHCARDS_FILE = "flashcards.csv"

# 3. LOAD EXISTING FLASHCARDS OR CREATE A NEW DATAFRAME
if os.path.exists(FLASHCARDS_FILE):
    flashcards_df = pd.read_csv(FLASHCARDS_FILE)
else:
    flashcards_df = pd.DataFrame(columns=["Word", "German explanation", "English translation", "Example sentence"])

# 4. FUNCTION TO CHECK IF WORD ALREADY EXISTS
def word_exists(word):
    return word.lower() in flashcards_df["Word"].str.lower().values

# 5. FUNCTION TO GENERATE FLASHCARD CONTENT
def generate_flashcard(word):
    prompt = f"""
    Create a flashcard for the German word '{word}'.
    Provide:
    - A short German explanation (in German, 1-2 sentences).
    - Its English translation.
    - A simple German example sentence using the word.

    Format:
    Word: {word}
    German explanation: ...
    English translation: ...
    Example sentence: ...
    """

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are a helpful German language tutor."},
            {"role": "user", "content": prompt}
        ]
    )

    return response.choices[0].message.content.strip()

# 6. FUNCTION TO SAVE FLASHCARD TO DATAFRAME & CSV
def save_flashcard(flashcard_text):
    lines = flashcard_text.split("\n")
    card_data = {}
    for line in lines:
        if ": " in line:
            key, value = line.split(": ", 1)
            card_data[key.strip()] = value.strip()

    flashcards_df.loc[len(flashcards_df)] = [
        card_data.get("Word", ""),
        card_data.get("German explanation", ""),
        card_data.get("English translation", ""),
        card_data.get("Example sentence", "")
    ]

    flashcards_df.to_csv(FLASHCARDS_FILE, index=False)
    print(f"Flashcard for '{card_data.get('Word', '')}' saved to {FLASHCARDS_FILE}.")

# 7. QUIZ FUNCTION
def quiz():
    if flashcards_df.empty:
        print("No flashcards available yet. Please add some words first.")
        return

    quiz_card = flashcards_df.sample(1).iloc[0]
    word = quiz_card["Word"]
    sentence = quiz_card["Example sentence"]
    correct_translation = quiz_card["English translation"]
    german_explanation = quiz_card["German explanation"]

    wrong_choices = flashcards_df[flashcards_df["English translation"] != correct_translation]["English translation"]
    if len(wrong_choices) >= 2:
        wrong_choices = random.sample(list(wrong_choices), 2)
    else:
        wrong_choices = [correct_translation, correct_translation]

    choices = [correct_translation] + wrong_choices
    random.shuffle(choices)

    print("\n--- QUIZ ---")
    print(f"German word: {word}")
    print(f"German sentence: {sentence}")
    print("What is the correct English translation?")
    for idx, choice in enumerate(choices, start=1):
        print(f"{idx}. {choice}")

    answer = input("Enter the number of your choice: ").strip()
    if answer.isdigit() and 1 <= int(answer) <= 3:
        chosen = choices[int(answer)-1]
        if chosen == correct_translation:
            print("Correct!")
        else:
            print(f"Wrong. The correct answer was: {correct_translation}")
        print(f"German explanation: {german_explanation}")
    else:
        print("Invalid choice.")

# 8. MAIN MENU
def main():
    print("German Flashcard Tool")
    while True:
        print("\nMenu:")
        print("1. Enter a new German word")
        print("2. Take a quiz")
        print("3. Exit")
        choice = input("Choose an option (1/2/3): ").strip()

        if choice == "1":
            word = input("Enter a new German word: ").strip()
            if word:
                if word_exists(word):
                    print(f"The word '{word}' is already in your flashcards list.")
                else:
                    flashcard = generate_flashcard(word)
                    print("\nGenerated Flashcard:\n")
                    print(flashcard)
                    save_flashcard(flashcard)
            else:
                print("Please enter a valid word.")
        elif choice == "2":
            quiz()
        elif choice == "3":
            print("Goodbye!")
            break
        else:
            print("Invalid choice. Please enter 1, 2, or 3.")

if __name__ == "__main__":
    main()
