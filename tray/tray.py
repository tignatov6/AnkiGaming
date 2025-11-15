from utils.anki_connect import hi as hi_anki
import config


def hi():
    print(f'hi from {__name__}')


if __name__ == "__main__":
    hi()
    hi_anki()
    
