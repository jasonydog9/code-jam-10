import PIL
import pygame

from puzzle import Puzzle


class ExamplePuzzle(Puzzle):
    """
    Summary

    This is an empty puzzle class, you can copy and paste to make different
    kinds of puzzles
    """

    def __init__(
        self,
        image: PIL.Image.Image,
        pieces_per_side: int,
        output_size: tuple[int, int] = (),
        puzzle_pos: tuple[int, int] = (0, 0),
    ):
        super().__init__(image, pieces_per_side, output_size, puzzle_pos)
        self.scramble()
        self.generate_orderlist()
        self.image_update()

    def loop(self, event: pygame.event):
        """
        Summary

        put code here to be run every event,
        such as an event loop to detect mouse clicks
        """
        pass

    def scramble(self):
        """Put the code to scramble your puzzle here"""
        pass
