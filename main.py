from utils.anki_connect import hi as hi_anki
import utils.config as config
import tray.tray as tray
import respawn_detect.respawn_detect as respawn_detect
import overlay.overlay as overlay
import app.app as app


def hi():
    print(f'hi from {__name__}')


if __name__ == "__main__":
    try:
        hi()
        hi_anki()
        config.hi()
        tray.hi()
        respawn_detect.hi()
        overlay.hi()
        app.hi()
    except Exception as e:
        print(e)
