from datetime import datetime
import random
from enum import Enum

import arcade

SCREEN_WIDTH = 1024
SCREEN_HEIGHT = 768
SPRITE_SCALING_COIN = 0.5
SPRITE_SCALING_PLAYER = 0.7
COIN_COUNT = 50
MOVEMENT_SPEED = 4


class CoinTypes(Enum):
    BRONZE = 0
    SILVER = 1
    GOLD = 2


class Player:
    def __init__(self, score, center_x, center_y):

        # Take the parameters of the init function above,
        # and create instance variables out of them.
        self.score = score
        self.speed = 0

        self.player_bounce_sound = arcade.load_sound("sounds/ball_bounce.wav")

        self.player_sprite = arcade.Sprite("images/player.png", SPRITE_SCALING_PLAYER)
        self.player_sprite.center_x = center_x
        self.player_sprite.center_y = center_y

    def draw(self):
        """ Draw the player with the instance variables we have. """
        self.player_sprite.draw()

    def update(self):
        # Move the player
        self.player_sprite.center_x += self.player_sprite.change_x
        self.player_sprite.center_y += self.player_sprite.change_y

        # See if the player hit the edge of the screen. If so, change direction
        if self.player_sprite.left < 0:
            self.player_sprite.change_x *= -1
            self.player_sprite.left = 0
            arcade.play_sound(self.player_bounce_sound)

        if self.player_sprite.right > SCREEN_WIDTH:
            self.player_sprite.change_x *= -1
            self.player_sprite.right = SCREEN_WIDTH
            arcade.play_sound(self.player_bounce_sound)

        if self.player_sprite.bottom < 0:
            self.player_sprite.change_y *= -1
            self.player_sprite.bottom = 0
            arcade.play_sound(self.player_bounce_sound)

        if self.player_sprite.top > SCREEN_HEIGHT:
            self.player_sprite.change_y *= -1
            self.player_sprite.top = SCREEN_HEIGHT
            arcade.play_sound(self.player_bounce_sound)

    def end_screen_spinning(self):
        self.player_sprite.angle -= 2
        # Spin me round
        if self.player_sprite.angle < 0:
            self.player_sprite.angle = 360


class Coin(arcade.Sprite):

    def __init__(self):
        coin_type = random.choice(list(CoinTypes))
        # Create the coin instance
        if coin_type == CoinTypes.SILVER:
            filename = "images/coinSilver.png"
            scale = SPRITE_SCALING_COIN / 2
            self.cost = 2
        elif coin_type == CoinTypes.GOLD:
            filename = "images/coinGold.png"
            scale = SPRITE_SCALING_COIN / 3
            self.cost = 3
        else:
            filename = "images/coinBronze.png"
            scale = SPRITE_SCALING_COIN
            self.cost = 1

        super().__init__(filename, scale)

        self.set_random_pos()

    def update(self):
        # Move the coin
        self.center_y -= self.cost

        # See if the coin has fallen off the bottom of the screen.
        # If so, reset it.
        if self.center_y < 0:
            self.set_random_pos()

        self.angle += 1
        # Spin me round
        if self.angle > 359:
            self.angle -= 360

    def set_random_pos(self):
        # Position the coin
        self.center_x = random.randrange(SCREEN_WIDTH - 5)
        self.center_y = random.randrange(SCREEN_HEIGHT - 5)


class Timer:
    def __init__(self, frames: int):
        self.frames = frames

    def draw(self):
        """ Draw the timer with the instance variables we have. """
        arcade.draw_text(
            f"Remaining time: {round(self.frames/60, 1)}",
            0,
            SCREEN_HEIGHT - 30,
            color=arcade.color.REDWOOD,
            font_size=15,
            width=SCREEN_WIDTH,
            align="center"
        )

    def update(self):
        """ update the timer with the instance variables we have. """
        if self.frames > 0:
            self.frames -= 1
        else:
            self.frames = 0


class MyGame(arcade.Window):

    def __init__(self, width, height, title):

        # Call the parent class's init function
        super().__init__(width, height, title)

        self.coin_list = None

        # Make the mouse disappear when it is over the window.
        # So we just see our object, not the pointer.
        self.set_mouse_visible(False)

        arcade.set_background_color(arcade.color.DAVY_GREY)

    def setup(self):
        """ Set up the game and initialize the variables. """

        # Sprite lists
        self.coin_list = arcade.SpriteList()

        self.coin_picked = arcade.load_sound("sounds/coin_picked.wav")
        self.coin_picked_player = None

        # Create the coins
        for i in range(COIN_COUNT):
            # Add the coin to the lists
            self.coin_list.append(Coin())

        # Set up the player
        self.player = Player(0, 50, 50)

        self.timer = Timer(frames=600)

    def on_draw(self):
        """ Called whenever we need to draw the window. """
        arcade.start_render()

        # Put the text on the screen.
        output = f"Score: {self.player.score}"
        arcade.draw_text(
            text=output,
            start_x=10,
            start_y=20,
            color=arcade.color.WHITE,
            font_size=12,
            width=SCREEN_WIDTH,
            align="left"
        )

        if self.timer.frames > 0:
            self.player.draw()
            self.coin_list.draw()
            self.timer.draw()
        else:
            self.player.player_sprite.center_x = SCREEN_WIDTH / 2
            self.player.player_sprite.center_y = SCREEN_HEIGHT / 2.5
            self.player.end_screen_spinning()
            self.player.draw()
            arcade.draw_text(
                "The End!",
                0,
                SCREEN_HEIGHT/2,
                font_size=10,
                width=SCREEN_WIDTH,
                align="center"
            )
            arcade.draw_text(
                "Press enter to start again.",
                0,
                SCREEN_HEIGHT/2-30,
                font_size=12,
                width=SCREEN_WIDTH,
                align="center"
            )

        arcade.draw_text(datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 5, SCREEN_HEIGHT - 10, font_size=8)

    def on_update(self, delta_time):
        if self.timer.frames > 0:
            self.player.update()
            self.coin_list.update()
            self.timer.update()
        coins_hit_list = arcade.check_for_collision_with_list(self.player.player_sprite, self.coin_list)
        # Loop through each colliding sprite, remove it, and add to the score.
        for coin in coins_hit_list:
            coin.set_random_pos()
            self.player.score += coin.cost
            self.player.speed += 1
            if not self.coin_picked_player or not self.coin_picked_player.playing:
                self.coin_picked_player = arcade.play_sound(self.coin_picked, volume=0.6)

    def on_key_press(self, key, modifiers):
        """ Called whenever the user presses a key. """
        if key == arcade.key.LEFT:
            self.player.player_sprite.change_x = -(MOVEMENT_SPEED + self.player.speed)
        elif key == arcade.key.RIGHT:
            self.player.player_sprite.change_x = (MOVEMENT_SPEED + self.player.speed)
        elif key == arcade.key.UP:
            self.player.player_sprite.change_y = (MOVEMENT_SPEED + self.player.speed)
        elif key == arcade.key.DOWN:
            self.player.player_sprite.change_y = -(MOVEMENT_SPEED + self.player.speed)
        elif key == arcade.key.ENTER:
            self.setup()
        elif key == arcade.key.ESCAPE:
            self.close()

    def on_key_release(self, key, modifiers):
        pass


def main():
    window = MyGame(SCREEN_WIDTH, SCREEN_HEIGHT, "Catch them all")
    window.setup()

    arcade.run()


main()
