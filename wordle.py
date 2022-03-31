import random

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time


class WordleDriver:

    def __init__(self):
        self.service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=self.service)
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
            'WINDY',
            'PAINT',
            'GOURD',
            'SWING',
            'AUDIO',
            'ARISE'
        ]
        self.five_letter_words = five_letter_words
        self.correct_word = "_____"
        self.letters_absent = []
        self.letters_present = {}
        self.guesses = []
        self.irow = 0

    def solver(self):

        while self.irow < len(self.game_rows):
            # God Speed :)
            guess = self.new_guess()
            self.input_guess(guess)
            time.sleep(2)

    def new_guess(self):
        if len(self.guesses) == 0:
            return random.choice(self.common_five_letter_words)

        else:
            # Check how the previous guess did
            tiles = self.get_tiles(self.irow - 1)

            for index, tile in enumerate(tiles):
                tile_div = tile.find_element(By.TAG_NAME, "div")
                evaluation = tile_div.get_attribute("evaluation")
                letter = tile_div.text.upper()

                if evaluation == "absent":
                    self.letters_absent.append(letter)

                elif evaluation == "present":
                    self.letters_present[letter] = index
                elif evaluation == "correct":
                    self.correct_word[index] = letter

    def input_guess(self, guess):
        keyboard = self.get_keyboard()

        for letter in guess:
            for key in keyboard:
                if key.text == letter:
                    key.click()

        for key in keyboard:
            if key.text == "ENTER":
                key.click()
                break

        if self.word_is_valid():
            self.irow += 1
            self.guesses.append(guess)

        else:
            self.five_letter_words.remove(guess)
            for key in keyboard:
                # Find the backspace
                if key.text == "":
                    for i in list(range(5)):
                        key.click()
                    break

    def word_is_valid(self):
        tiles = self.get_tiles(self.game_rows[self.irow])

        for tile in tiles:
            tile_div = tile.find_element(By.TAG_NAME, "div")

            if tile_div.get_attribute("data-state") == "tbd":
                return False
            else:
                return True

    # TODO: CREATE METHOD FOR NEW GUESS


if __name__ == "__main__":
    wordle = WordleDriver()
    wordle.driver.quit()

