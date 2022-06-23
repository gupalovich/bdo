import math
import random

from time import sleep

from threading import Thread, Lock

from .bot import BotState
from .vision import Vision
from .utils import wind_mouse_move_camera, calc_rect_middle


class Camera:
    """Manage ingame bot camera by giving Vision character object"""
    # threading properties
    stopped = True
    lock = None
    # properties
    state = None
    screen = None
    screen_size = (1920, 1080)
    targets = []
    character_position = []
    main_loop_delay = 0.04
    # constants
    INITIALIZING_SECONDS = 1

    def __init__(self, character: Vision):
        # create a thread lock
        self.lock = Lock()
        # properties
        self.character = character

    def choose_target(self, targets: list[tuple]) -> tuple:
        """Choose middle target from targets"""
        index = math.floor(len(targets) / 2)
        index = index - 1 if len(targets) % 2 == 0 else index
        return targets[index]

    def follow_target(self, rect: tuple) -> None:
        """Camera follow given target coords"""
        screen_w, screen_h = self.screen_size
        x, y, w, h = calc_rect_middle(rect)
        move_x = int(x - (screen_w / 2))
        move_y = int(y - (screen_h / 3))
        if abs(move_x) < 50 and abs(move_y) < 50:
            return None
        overhead = 35
        move_x = move_x + overhead if move_x > 0 else move_x - overhead
        wind_mouse_move_camera(move_x, 0, step=20)

    def move_around(self) -> None:
        """Move camera around"""
        move_range = random.randint(-300, 250)
        wind_mouse_move_camera(move_range, 0, step=15)

    def adjust_angle(self, rect: tuple) -> None:
        """Adjust camera angle by character position on screen"""
        x, y, w, h = calc_rect_middle(rect)
        target_y = 465
        move_y = -int(y - target_y)
        if abs(move_y) <= 4:
            return
        overhead = 70
        move_y = move_y + overhead if move_y > 0 else move_y - overhead
        wind_mouse_move_camera(0, move_y)

    def update_targets(self, targets: list[tuple]) -> None:
        """Threading method: update targets property"""
        self.lock.acquire()
        self.targets = targets
        self.lock.release()

    def update_screen(self, screen: object) -> None:
        """Threading method: update screen property"""
        self.lock.acquire()
        self.screen = screen
        self.lock.release()

    def update_state(self, state: object) -> None:
        """Threading method: update screen property"""
        self.lock.acquire()
        self.state = state
        self.lock.release()

    def start(self):
        self.stopped = False
        t = Thread(target=self.run)
        t.start()

    def stop(self):
        self.stopped = True

    def run(self):
        sleep(self.INITIALIZING_SECONDS)
        while not self.stopped:
            # camera adjustment by target
            if self.targets:
                target = self.choose_target(self.targets)
                self.follow_target(target)
                sleep(0.3)
            else:
                pass
                # self.move_around()
            # camera adjustment by character
            self.character_position = self.character.find(self.screen, threshold=0.8)
            if self.character_position:
                self.adjust_angle(self.character_position[0])

            if self.state == BotState.INIT:
                pass
            elif self.state == BotState.SEARCHING:
                pass
            elif self.state == BotState.NAVIGATING:
                pass
            elif self.state == BotState.KILLING:
                pass