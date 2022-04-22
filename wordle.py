import random

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time


# TODO: KEEP TRACK OF SCORE (CSV FILE?? date, final_guess, total score (n/5)
# TODO: WHEN EVALUATING LETTERS, SEE IF ITS ALREADY IN A CATEGORY.. WILL HELP WITH GUESSING.
# TODO: QUIT DRIVER IF RUN OUT OF GUESS WORDS
# TODO: QUIT DRIVER IF COULD NOT GUESS WORD


class WordleDriver:

    def __init__(self):
        self.service = Service(ChromeDriverManager().install())
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument("--headless")
        self.driver = webdriver.Chrome(service=self.service, options=chrome_options)
        self.url = 'https://www.nytimes.com/games/wordle/index.html'
        self.driver.get(self.url)
        self.game_app = self.expand_shadow_element(self.driver.find_element(By.TAG_NAME, "game-app"))
        self.game_rows = self.game_app.find_elements(By.TAG_NAME, "game-row")
        time.sleep(2)
        self.close_instructions()

    def close_instructions(self):
        root2 = self.expand_shadow_element(self.game_app.find_element(By.TAG_NAME, "game-modal"))
        close_icon = root2.find_element(By.CSS_SELECTOR, 'div.close-icon')
        close_icon.click()

    def expand_shadow_element(self, element):
        shadow_root = self.driver.execute_script('return arguments[0].shadowRoot', element)
        return shadow_root

    def get_keyboard(self):
        keyboard = self.game_app.find_element(By.TAG_NAME, "game-keyboard")
        keyboard_shadow = self.expand_shadow_element(keyboard)
        letters = keyboard_shadow.find_elements(By.TAG_NAME, 'button')

        return letters

    def get_tiles(self, game_row):
        game_row_shadow = self.expand_shadow_element(game_row)
        tile_elements = game_row_shadow.find_elements(By.TAG_NAME, "game-tile")
        tiles = []

        for tile in tile_elements:
            tiles.append(self.expand_shadow_element(tile))

        return tiles


class WordleSolver(WordleDriver):

    def __init__(self, five_letter_words: list):
        super().__init__()
        self.common_five_letter_words = [
            'FRAME',
            'GRAZE',
            'PAINT',
            'GOURD',
            'SWING',
            'AUDIO',
            'ARISE',
            'WINDY'
        ]
        self.five_letter_words = five_letter_words
        self.correct_word = ["_", "_", "_", "_", "_"]
        self.letters_absent = []
        self.letters_present = {}
        self.guesses = []
        self.i_row = 0

    def solve(self):
        guess = "_____"

        while self.i_row < len(self.game_rows) and guess is not None:
            print(f"Guess # {self.i_row + 1}")
            print(f"Length of valid five letter words: {len(self.five_letter_words)}")
            print(f"Letters absent: {', '.join(self.letters_absent)}")
            print(f"Letters present: {', '.join(self.letters_present.keys())}")
            print(f"Valid words: {', '.join(self.five_letter_words)}")
            guess = self.new_guess()
            print(f"Guess word: {guess}")
            self.input_guess(guess)
            print("")

            if "_" not in self.correct_word:
                print(f"You won!\nCorrect word: {''.join(self.correct_word)}")
                self.driver.quit()
                break
        self.driver.quit()

    def new_guess(self):
        if len(self.guesses) == 0:
            guess = random.choice(self.common_five_letter_words)

        else:
            try:
                guess = random.choice(self.five_letter_words)
            except IndexError:
                print(f"Looks like you've run out guesses. \nLast guessed word: {self.guesses[-1]}")
                print(f"Correct word structure: {''.join(self.correct_word)}")
                guess = None

        return guess

    def input_guess(self, guess):
        keyboard = self.get_keyboard()

        for letter in guess:
            for key in keyboard:
                if key.text == letter:
                    key.click()

        for key in keyboard:
            if key.text == "ENTER":
                key.click()
                time.sleep(2.5)
                break

        if self.word_is_valid():
            self.i_row = self.i_row + 1
            self.guesses.append(guess)
            self.evaluate_guess()
            self.five_letter_words.remove(guess)
            self.remove_invalid_words()

        else:
            self.five_letter_words.remove(guess)
            print("Invalid Guess Word")
            for key in keyboard:
                # Find the backspace
                if key.text == "":
                    for _ in list(range(5)):
                        key.click()
                        time.sleep(0.2)
                    break

    def word_is_valid(self):
        valid = True
        tiles = self.get_tiles(self.game_rows[self.i_row])

        for tile in tiles:
            tile_div = tile.find_element(By.TAG_NAME, "div")

            if tile_div.get_attribute("data-state") == "tbd":
                valid = False
            else:
                continue
        return valid

    def evaluate_guess(self):
        tiles = self.get_tiles(self.game_rows[self.i_row - 1])

        # Get the evaluations from the tiles
        for index, tile in enumerate(tiles):
            tile_div = tile.find_element(By.TAG_NAME, "div")
            evaluation = tile_div.get_attribute("data-state")
            letter = tile_div.text.upper()

            if evaluation == "absent":
                self.letters_absent.append(letter)

            elif evaluation == "present":
                self.letters_present[letter] = index

            elif evaluation == "correct":
                self.correct_word[index] = letter

        print(f"Correct word: {''.join(self.correct_word)}")

    def find_invalid_words(self):
        words_to_remove = []

        for word in self.five_letter_words:
            # Check if matches the correct word
            for i in list(range(5)):
                if self.correct_word[i] == "_":
                    continue
                elif self.correct_word[i] == word[i]:
                    continue
                else:
                    words_to_remove.append(word)

            if word in words_to_remove:
                continue

            # Check if letter is truly absent and in word:
            for letter in self.letters_absent:

                if letter in word:
                    if letter in self.correct_word:
                        if self.correct_word.index(letter) == word.index(letter):
                            continue
                        else:
                            words_to_remove.append(word)
                    elif letter in self.letters_present.keys():
                        continue
                    else:
                        words_to_remove.append(word)
                else:
                    continue

            if word in words_to_remove:
                continue

            # Check if letter present is in word
            for letter in self.letters_present.keys():
                if letter in word:
                    if self.letters_present[letter] == word.index(letter):
                        words_to_remove.append(word)
                else:
                    words_to_remove.append(word)

            if word in words_to_remove:
                continue

        return words_to_remove

    def remove_invalid_words(self):

        words_to_remove = self.find_invalid_words()

        for word in words_to_remove:
            try:
                self.five_letter_words.remove(word)
            except ValueError:
                continue


if __name__ == "__main__":
    from english_words import english_words_lower_set

    five_letter_word = []
    correct_word = {}
    incorrect_placement = {}

    special_char = "*-'[{]}\|!^&()%$#,.?/><"
    # Only use 5 letter words
    for words in english_words_lower_set:
        if len(words) == 5:
            for char in special_char:
                if char in words:
                    break
                elif char == special_char[-1]:
                    five_letter_word.append(words.upper())
        else:
            continue
    five_letter_word.append("LOWLY")
    five_letter_word.append("FEWER")

    wordle = WordleSolver(five_letter_word)
    wordle.solve()
