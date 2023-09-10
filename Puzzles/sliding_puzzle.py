import random
import typing

import numpy as np
import PIL
import pygame

from helpers import EventHandler, EventTypes
from puzzle import Puzzle


class SlidingPuzzle(Puzzle):
    """Container class for the Sliding Puzzle"""

    UP = (0, -1)
    DOWN = (0, 1)
    LEFT = (-1, 0)
    RIGHT = (1, 0)
    NO_MOVE = (0, 0)

    def __init__(
        self,
        image: PIL.Image.Image,
        pieces_per_side: int,
        output_size: tuple[int, int],
        puzzle_pos: tuple[int, int] = (0, 0),
    ):
        super().__init__(image, pieces_per_side, output_size, puzzle_pos)
        self.scramble()
        self.image_update()

    def scramble(self):
        """
        Summary

        Removes the last piece of puzzle, shuffles the puzzle, and then re-inserts
        the last puzzle piece.
        """
        self.orderlist.pop()
        self.last_piece = self.pieces.pop()
        self.last_image = self.last_piece.image
        self.last_piece.image = np.full(
            self.pieces[0].image.shape, fill_value=0, dtype=np.uint8
        )
        temp_list = self.orderlist.copy()
        while temp_list == self.orderlist:
            random.shuffle(self.orderlist)
            if not self.solvable(self.orderlist):
                self.orderlist[-1], self.orderlist[-2] = (
                    self.orderlist[-2],
                    self.orderlist[-1],
                )
        self.orderlist.append(self.total_pieces - 1)
        self.pieces.append(self.last_piece)
        for pos, i in enumerate(self.orderlist):
            self.pieces[i].relative_y, self.pieces[i].relative_x = divmod(
                pos, self.pieces_per_side
            )

    def loop(self, event: pygame.event.Event):
        """Loop to be run at every event to see how the puzzle should react"""
        if event.type == pygame.MOUSEBUTTONUP:
            mouse_start = pygame.mouse.get_pos()
            temp = self.get_tile_index_from_pos(mouse_start)
            if temp is not None:
                self.move(self.tile_can_move(temp))

    def tile_can_move(self, tile_index: int):
        """
        Summary

        Takes a given tile index and detects if the last (blank) tile is in that row.
        If it finds it, it returns the tiles that can move and the direction they can
        move in
        """
        # Get tiles in row
        orderlist_index_start = (
            tile_index // self.pieces_per_side * self.pieces_per_side
        )
        orderlist_index_end = (
            tile_index // self.pieces_per_side * self.pieces_per_side
            + self.pieces_per_side
        )
        column_number = tile_index % self.pieces_per_side
        orderlist_column = [
            self.orderlist[column_number + i * self.pieces_per_side]
            for i in range(self.pieces_per_side)
        ]
        orderlist_row = self.orderlist[orderlist_index_start:orderlist_index_end]
        if self.total_pieces - 1 in orderlist_column:
            zero_index = orderlist_column.index(self.total_pieces - 1)
            tile_index_relative = tile_index // self.pieces_per_side
            delta = zero_index - tile_index_relative
            if delta == 0:
                return SlidingPuzzle.NO_MOVE, [], tile_index
            direction = SlidingPuzzle.UP if delta < 0 else SlidingPuzzle.DOWN
            indices: typing.Sequence[int] = [
                column_number + i * self.pieces_per_side
                for i in range(self.pieces_per_side)
            ]
        elif self.total_pieces - 1 in orderlist_row:
            zero_index = orderlist_row.index(self.total_pieces - 1)
            tile_index_relative = tile_index % self.pieces_per_side
            delta = zero_index - tile_index_relative
            if delta == 0:
                return SlidingPuzzle.NO_MOVE, [], tile_index
            direction = SlidingPuzzle.LEFT if delta < 0 else SlidingPuzzle.RIGHT
            indices = range(orderlist_index_start, orderlist_index_end)
        else:
            return SlidingPuzzle.NO_MOVE, [], tile_index

        movable = [
            indices[i]
            for i in range(
                tile_index_relative, zero_index, [i for i in direction if i != 0][0]
            )
        ]
        return direction, movable, tile_index

    def move(self, direction_tile_list_origin_tile: tuple[tuple[int, int], list, int]):
        """
        Summary

        Given the list of tiles, the move direction, and the originating tile,
        this function changes the relative_x and relative_y of pieces to cause
        puzzle shifts
        """
        direction, tile_list, origin_tile = direction_tile_list_origin_tile
        if direction == SlidingPuzzle.NO_MOVE:
            return 0
        for i in tile_list:
            self.pieces[self.orderlist[i]].relative_x += direction[0]
            self.pieces[self.orderlist[i]].relative_y += direction[1]
        self.generate_orderlist_given_tile(origin_tile)
        if self.orderlist == list(range(self.total_pieces)):
            EventHandler.add(EventTypes.PUZZLE_SOLVED)
            self.pieces[-1].image = self.last_image
        self.image_update()

    def generate_orderlist_given_tile(self, origin_tile: int):
        """
        Summary

        Different generate_orderlist function that generates an orderlist
        and moves the blank tile to the tile that the player clicked on
        """
        for i in self.pieces:
            if i.absolute_index == self.total_pieces - 1:
                i.relative_y = origin_tile // self.pieces_per_side
                i.relative_x = origin_tile % self.pieces_per_side
                i.relative_index = origin_tile
                continue

            i.relative_index = i.relative_y * self.pieces_per_side + i.relative_x
            self.orderlist[i.relative_index] = i.absolute_index
        self.orderlist[origin_tile] = self.total_pieces - 1

    def solvable(self, unsorted: list[int]):
        """
        Summary

        This function performs inversion counting on a list.
        If the number of inversions is even, then the puzzle is solvable
        """
        inversions = 0
        for j in range(self.total_pieces - 1):
            for i in range(j + 1, self.total_pieces - 1):
                if unsorted[j] > unsorted[i]:
                    inversions += 1
        return inversions % 2 == 0
