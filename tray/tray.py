# для импорта модулей из корня проекта
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utils.anki_connect import hi as hi_anki
import utils.config as config


def hi():
    print(f'hi from {__name__}')


if __name__ == "__main__":
    hi()
    hi_anki()
    config.hi()
