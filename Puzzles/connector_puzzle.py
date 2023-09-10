import random

import numpy as np
import PIL
import pygame

from helpers import EventHandler, EventTypes
from puzzle import Puzzle

COLORS = [
    (0xFF, 0xFF, 0xFF),
    (0xFF, 0x00, 0x00),
    (0x00, 0xFF, 0x00),
    (0x00, 0x00, 0xFF),
]


class Connector(Puzzle):
    """
    Summary

    This is the connector puzzle, where you click pieces to change their color.
    """

    def __init__(
        self,
        # not required:
        image: PIL.Image.Image,
        pieces_per_side: int,
        output_size: tuple[int, int],
        puzzle_pos: tuple[int, int] = (0, 0),
    ):
        real_image = PIL.Image.new(image.mode, image.size, color=0xFFFFFF)
        super().__init__(real_image, pieces_per_side, output_size, puzzle_pos)
        self.color_list = [COLORS[0]] * self.total_pieces
        self.locked = [False] * self.total_pieces
        self.scramble()
        self.generate_orderlist()
        self.image_update()

    def loop(self, event: pygame.event.Event):
        """Put your loop code here"""
        if event.type == pygame.MOUSEBUTTONUP:
            tile = self.get_tile_index_from_pos(pygame.mouse.get_pos())
            self.click_tile(tile, event.button == 3)
            self.image_update()
            EventHandler.add(EventTypes.PUZZLE_SPRITE_UPDATE)

            if self.is_solved():
                EventHandler.add(EventTypes.PUZZLE_SOLVED)

    def click_tile(self, tile: int, reverse: bool):
        """Change the colors of a tile"""
        if self.locked[tile]:
            return

        direction = -1 if reverse else 1
        color_idx = (COLORS.index(self.color_list[tile]) + direction) % len(COLORS)
        self.color_list[tile] = COLORS[color_idx]
        shape = self.pieces[tile].image.shape

        self.pieces[tile].image = np.reshape(
            np.tile(
                self.color_list[tile],
                shape[0] * shape[1],
            ),
            shape,
        )

    def is_solved(self) -> bool:
        """Check whether the connector puzzle is solved."""
        tiles = np.reshape(
            [COLORS.index(c) for c in self.color_list],
            (self.pieces_per_side, self.pieces_per_side),
        )
        # essentially, confirm that every piece of a color (other than white) is
        # connected
        for i in range(1, len(COLORS)):
            # turn into an array of True / False
            locations = np.argwhere(tiles == i)
            connected = set()

            if len(locations) < 2:
                continue

            connected.add(tuple(locations[0]))
            locs = set(map(tuple, locations[1:]))
            checking = [locations[0]]
            while checking:
                location = checking.pop()
                for neighbor in (
                    location + (1, 0),
                    location + (0, 1),
                    location + (-1, 0),
                    location + (0, -1),
                ):
                    if tuple(neighbor) in locs and tuple(neighbor) not in connected:
                        connected.add(tuple(neighbor))
                        checking.append(neighbor)

            if len(locations) != len(connected):
                return False

        return True

    def scramble(self) -> None:
        """Put the code to scramble your puzzle here"""
        # for _ in range(self.total_pieces):
        #     self.invert(self.get_neighbors(random.randint(0, self.total_pieces - 1)))
        for i in range(self.total_pieces):
            # TODO: this might not be solve-able
            if random.random() < 0.10:
                for _ in range(int(random.random() * 4)):
                    self.click_tile(i, False)
                self.locked[i] = True
        self.image_update()
