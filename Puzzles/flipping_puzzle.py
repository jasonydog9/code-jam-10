import pygame, sys
from pygame.locals import QUIT
import numpy as np
import random

import PIL


from puzzle import Puzzle

class FlippingPuzzle(Puzzle):

    def __init__(
            self,
            image: PIL.Image,
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
        for i in range(self.total_pieces):
            rotations=random.randint(0,3)
            for j in range(rotations):
                self.flip(i)
        if Puzzle.SOLVED in self.event:
            self.scramble()
            self.event.remove(Puzzle.SOLVED)
        self.image_update()

    def flip(self, tile):
        self.pieces[tile].image = np.flip(self.pieces[tile].image,1)

        self.image_update()
        one = np.array(pygame.surfarray.array3d(self.image))
        two = np.array(PIL.Image.open('sample_images/Monalisa.png').resize(self.output_size)).swapaxes(0,1)
        if np.array_equal(one,two):
            self.event.append(Puzzle.SOLVED)


