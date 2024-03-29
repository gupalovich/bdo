import cv2 as cv  # noqa isort:skip
import logging

from modules.bot import BlackDesertBot, BotBuffer, BotState
from modules.camera import Camera
from modules.keys import KeyListener
from modules.utils import grab_screen, load_config
from modules.vision import Vision

from time import sleep  # noqa isort:skip


if __name__ == "__main__":
    config = load_config()
    DEBUG = config.getboolean("MAIN", "DEBUG")

    if config["MAIN"]["DEBUG"]:
        logging.basicConfig(
            level=logging.INFO, format="%(name)s - %(levelname)s - %(message)s"
        )
        logging.info("DEBUG")
    else:
        pass

    vision = Vision()
    bot = BlackDesertBot()
    bot_buffer = BotBuffer(bot.buffs + bot.foods)
    camera = Camera()
    threads = [bot, bot_buffer, camera]
    key_listener = KeyListener(to_stop=threads)
    bot.start()
    bot_buffer.start()
    camera.start()

    running = False
    while True:
        try:
            screen = grab_screen(region=[0, 0, 1920, 1080])
            buff_queue = bot_buffer.buff_queue
            targets = vision.find_ui(screen, "vessel")
            character_position = camera.character_position

            if bot.state == BotState.REPAIRING or bot.state == BotState.STASHING:
                targets = []

            bot.update_screen(screen)
            bot.update_buff_queue(buff_queue)
            bot.update_targets(targets)
            bot.update_character_position(character_position)

            bot_buffer.update_screen(screen)

            camera.update_state(bot.state)
            camera.update_screen(screen)
            camera.update_targets(targets)

            bot.filter_ability_cooldowns()

            if DEBUG:
                result = targets + character_position
                screen = vision.draw_rectangles(
                    cv.cvtColor(screen, cv.COLOR_BGR2RGB), result
                )
                screen = cv.resize(screen, (1200, 675))
                cv.imshow("Screen", screen)
                if cv.waitKey(1) == ord("q"):
                    [thread.stop() for thread in threads]
                    cv.destroyAllWindows()
                    break
            else:
                if not running:
                    key_listener.start()
                    running = True
                if key_listener.pause:
                    print("- Pause")
                    sleep(1)
                if key_listener.stopped:
                    print("- Main loop stopped")
                    break
            sleep(bot.main_loop_delay)
        except Exception as e:
            [thread.stop() for thread in threads]
            raise e
