import random

import numpy as np
import PIL
import pygame

from puzzle import Puzzle


class FlippingPuzzle(Puzzle):
    """Summary: breaks tiles into pieces and scrambles them by flipping them"""

    def __init__(
        self,
        image: PIL.Image.Image,
        pieces_per_side: int,
        output_size: tuple[int, int] = (),
        puzzle_pos: tuple[int, int] = (0, 0),
    ):
        super().__init__(image, pieces_per_side, output_size, puzzle_pos)
        self.old_image = self.image
        self.scramble()
        self.image_update()

    def loop(self, event: pygame.event):
        """Put your loop code here"""
        if event.type == pygame.MOUSEBUTTONUP:
            tile = self.get_tile_index_from_pos(pygame.mouse.get_pos())
            self.flip(tile)
            self.image_update()
            self.event.append(Puzzle.UPDATE)
        pass

    def scramble(self):
        """Flips puzzle pieces randomly"""
        for i in range(self.total_pieces):
            rotations = random.randint(0, 1)
            if rotations == 1:
                self.flip(i)
        if Puzzle.SOLVED in self.event:
            self.scramble()
            self.event.remove(Puzzle.SOLVED)
        self.image_update()

    def flip(self, tile):
        """If tile is clicked it flips the piece and compares the updated image

        to original to see if its correct
        """
        self.pieces[tile].image = np.flip(self.pieces[tile].image, 1)

        self.image_update()
        one = np.array(pygame.surfarray.array3d(self.image))
        two = np.array(
            PIL.Image.open("sample_images/Monalisa.png").resize(self.output_size)
        ).swapaxes(0, 1)
        if np.array_equal(one, two):
            self.event.append(Puzzle.SOLVED)
