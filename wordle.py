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
        time.sleep(3)
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


if __name__ == "__main__":
    wordle = WordleDriver()
    wordle.driver.quit()

