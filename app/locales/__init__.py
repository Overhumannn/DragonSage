import json
import os

base_dir = os.path.dirname(__file__)

def load_language(lang_code):
    with open(os.path.join(base_dir, f"{lang_code}.json"), "r", encoding="utf-8") as file:
        return json.load(file)

languages = {
    "ru": load_language("ru"),
    "en": load_language("en")
}