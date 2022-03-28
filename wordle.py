from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from english_words import english_words_lower_alpha_set
import time


class WordleDriver:

    def __init__(self):
        self.service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=self.service)
        self.url = 'https://www.nytimes.com/games/wordle/index.html'
        self.driver.get(self.url)
        time.sleep(3)
        self.close_instructions()

    def close_instructions(self):
        root1 = self.expand_shadow_element(self.driver.find_element(By.TAG_NAME, "game-app"))
        root2 = self.expand_shadow_element(root1.find_element(By.TAG_NAME, "game-modal"))
        close_icon = root2.find_element(By.CSS_SELECTOR, 'div.close-icon')
        close_icon.click()

    def expand_shadow_element(self, element):
        shadow_root = self.driver.execute_script('return arguments[0].shadowRoot', element)
        return shadow_root


if __name__ == "__main__":
    wordle = WordleDriver()
    wordle.driver.quit()

