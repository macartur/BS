# -*- coding utf-8 -*-
from FGAme import listen, World, color
from button import Button
from ball import Ball
from pointer import Pointer
from mathtools import Vec2
from scene import Scene, SCREEN_MIDDLE
from goal import Goal
from random import randint
import status
import state

TEAM_SIZE = 4
TEAM_A_POSITIONS = ((SCREEN_MIDDLE[0] - 100, SCREEN_MIDDLE[1] + 200),
                    (SCREEN_MIDDLE[0] - 100, SCREEN_MIDDLE[1] - 200),
                    (SCREEN_MIDDLE[0] - 230, SCREEN_MIDDLE[1] + 70),
                    (SCREEN_MIDDLE[0] - 230, SCREEN_MIDDLE[1] - 70),)

TEAM_B_POSITIONS = ((SCREEN_MIDDLE[0] + 100, SCREEN_MIDDLE[1] + 200),
                    (SCREEN_MIDDLE[0] + 100, SCREEN_MIDDLE[1] - 200),
                    (SCREEN_MIDDLE[0] + 230, SCREEN_MIDDLE[1] + 70),
                    (SCREEN_MIDDLE[0] + 230, SCREEN_MIDDLE[1] - 70),)


class ButtonSoccer(World):

    def __init__(self):
        World.__init__(self)
        self.add(Scene())
        self.force = Vec2(0, 0)
        self.add_bounds(width=10)
        self.buttons_team_a = []
        self.buttons_team_b = []
        self.create_buttons()
        self.create_goal()
        self.register_listener()
        self.current_team = None

        self.ball = Ball()
        self.add(self.ball)

    def create_goal(self):
        self.goals = list()
        self.goals.append(Goal("RIGHT"))
        self.goals.append(Goal("LEFT"))

        for gol in self.goals:
            for dash in gol.elements():
                self.add(dash)

    def create_buttons(self):
        self.buttons_team_a = self.create_team('blue', TEAM_A_POSITIONS)
        self.buttons_team_b = self.create_team('red', TEAM_B_POSITIONS)

        if randint(1, 11) % 2 == 0:
            self.change_availability(self.buttons_team_a)
        else:
            self.change_availability(self.buttons_team_b)

    def create_team(self, team_color, team_positions):
        buttons = []
        for position in team_positions:
            button = Button(team_color)
            button.pos = position
            buttons.append(button)
            self.add(button)
        return buttons

    def change_turn(self):
        self.change_availability(self.buttons_team_a)
        self.change_availability(self.buttons_team_b)

    def change_availability(self, team):
        for button in team:
            if button.current_status is status.AVAILABLE:
                button.current_status = status.UNAVAILABLE
                button.color = color.Color(100, 100, 100)
            elif button.current_status is status.UNAVAILABLE:
                button.current_status = status.AVAILABLE
                button.color = button.team_color

    @listen('mouse-long-press', 'left')
    def update_poiter(self, pos):
        self.clear_pointer()
        for button in self.buttons_team_a + self.buttons_team_b:
            if button.current_state is state.CLICKED:
                try:
                    size = button.pos - Vec2(pos)
                    p = Pointer(button.pos.as_tuple(), size.as_tuple())
                    self.add(p)
                except ZeroDivisionError:
                    pass

    def clear_pointer(self):
        for element in self.get_render_tree().walk():
            if isinstance(element, Pointer):
                self.remove(element)

    @listen('frame-enter')
    def force_bounds(self):
        self.ball.update_forces()
        for button in self.buttons_team_a + self.buttons_team_b:
            button.update_forces()

    @listen('frame-enter')
    def check_goal(self):
        for goal in self.goals:
            if goal.is_goal(self.ball.pos):
                print("GOOOOOOOOOOOOOOOOL")

    def get_current_team(self, button):
        if button in self.buttons_team_a:
            self.current_team = self.buttons_team_a
        else:
            self.current_team = self.buttons_team_b

    def end_turn(self):
        stopped = []
        for button in self.buttons_team_a + self.buttons_team_b:
            if button.current_state is state.MOVING:
                stopped.append(False)
            if button.current_state is state.STOPPED:
                stopped.append(True)

        if False not in stopped:
            self.change_turn()

    def register_listener(self):
        for button in self.buttons_team_a + self.buttons_team_b:
            button.listen('released', self.get_current_team, button)
            button.listen('released', self.clear_pointer)
            button.listen('stopped', self.end_turn)

if __name__ == '__main__':
    game = ButtonSoccer()
    game.run()
