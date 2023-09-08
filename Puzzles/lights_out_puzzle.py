import random

import numpy as np
import PIL
import pygame

from puzzle import Puzzle


class LightsOut(Puzzle):
    """
    Summary

    This is the Lights Out puzzle, where every piece you click on
    causes neighboring to invert
    """

    def __init__(
        self,
        image: PIL.Image.Image,
        pieces_per_side: int,
        output_size: tuple[int, int] = (),
        puzzle_pos: tuple[int, int] = (0, 0),
    ):
        super().__init__(image, pieces_per_side, output_size, puzzle_pos)
        self.light_list = [False] * self.total_pieces
        self.scramble()
        self.generate_orderlist()
        self.image_update()

    def loop(self, event: pygame.event):
        """Put your loop code here"""
        if event.type == pygame.MOUSEBUTTONUP:
            tile = self.get_tile_index_from_pos(pygame.mouse.get_pos())
            neighbors = self.get_neighbors(tile)
            self.invert(neighbors)
            self.image_update()
            self.event.append(Puzzle.UPDATE)
        pass

    def invert(self, inverted_tiles: list[int]):
        """Invert the colors of any tile in the list"""
        if not isinstance(inverted_tiles, int):
            pass
        else:
            temp_list = []
            temp_list.append(inverted_tiles)
            inverted_tiles = temp_list.copy()
        for i in inverted_tiles:
            self.light_list[i] = False if self.light_list[i] else True
            self.pieces[i].image = np.multiply(
                self.pieces[i].image,
                np.full(self.pieces[i].image.shape, fill_value=-1, dtype=np.uint8),
            )
        if self.light_list == [False] * self.total_pieces:
            self.event.append(Puzzle.SOLVED)

    def get_neighbors(self, tile: int):
        """Find the neighbors of a given tile"""
        neighbors = [tile]
        if tile % self.pieces_per_side != 0:
            neighbors.append(tile - 1)
        if tile % self.pieces_per_side != self.pieces_per_side - 1:
            neighbors.append(tile + 1)
        if tile // self.pieces_per_side != 0:
            neighbors.append(tile - self.pieces_per_side)
        if tile // self.pieces_per_side != self.pieces_per_side - 1:
            neighbors.append(tile + self.pieces_per_side)
        return neighbors

    def scramble(self):
        """Put the code to scramble your puzzle here"""
        for _ in range(self.total_pieces):
            self.invert(self.get_neighbors(random.randint(0, self.total_pieces - 1)))
        if Puzzle.SOLVED in self.event:
            self.scramble()
            self.event.remove(Puzzle.SOLVED)
        self.image_update()
