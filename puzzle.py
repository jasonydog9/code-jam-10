import numpy as np
import PIL

from helpers import EventHandler, EventTypes, make_2d_surface_from_array


class Puzzle:
    """Parent class Puzzle

    All image puzzles are a subset of this class. This class splits a
    puzzle image up into individual pieces that can be modified, moved, and deleted.
    This module assumes that puzzles will have the same number of pieces tall as they
    are wide, so rectangular puzzles will have rectangular pieces.

    Args:
        image:
            A PIL image, returned by Image.open('some_image_file.png').

        pieces_per_side:
            Determines how many pieces the puzzle is cut into.
            will slightly shrink the image if the pieces cannot fit evenly into it.
            ^^^ This will leave a border around the image

        output_size:
            This is the size of the image as displayed on the screen.

        puzzle_pos:
            this is used to determine which piece was clicked when
            the puzzle is not in the top-left corner of the window.

    Attributes:
        pieces_per_side:
            This is the number of pieces on any given section of the puzzle (see below)
            if pieces_per_side is 5:
                puzzle looks like:
                       r * * * * *
                       | * * * * *
               5 pieces| * * * * *
                       | * * * * *
                       L * * * * *
            and total_pieces is 25.

        image:
            this is how the puzzle currently looks.
            On initialization the puzzle looks like the input image.

        orderlist:
            This is a list of length total_pieces containing the order of the pieces.
            For instance if pieces_per_side is 2, then orderlist starts as [0, 1, 2, 3]
            [ 0 , 1 ,
              2 , 3 ]
            swapping the top two pieces:
            orderlist is [1, 0, 2, 3]
            puzzle looks like:
            [ 1 , 0 ,
              2 , 3 ]
    """

    def __init__(
        self,
        image: PIL.Image.Image,
        pieces_per_side: int,
        output_size: tuple[int, int],
        puzzle_pos: tuple[int, int],
    ):
        if type(image) is not PIL.PngImagePlugin.PngImageFile:
            raise (
                TypeError(
                    "Expected type "
                    + str(PIL.PngImagePlugin.PngImageFile)
                    + ", got type "
                    + str(type(image))
                    + " instead."
                )
            )
        self.output_size = output_size
        self.pieces_per_side = pieces_per_side
        self.total_pieces = pieces_per_side**2
        self.image, self.shape, self.pieces = self.modify_image(image, output_size)
        self.orderlist = list(range(0, self.total_pieces))
        self.puzzle_x, self.puzzle_y = puzzle_pos

    def modify_image(self, image: PIL.Image.Image, output_size: tuple[int, int]):
        """Resizes the input image to the output size.

        Splits the image into total_pieces parts, then creates a PuzzlePiece object from
        the image. PuzzlePiece object is stored in a list called pieces. Raises an
        Exception if the resized image cannot be divided into total_pieces without
        remainder.

        Raises:
            SomeException: resized image cannot be divided into total_pieces without
            remainder  TODO: What exception?
        """
        if output_size:
            image = image.resize(output_size)
        image = image.resize(
            (
                image.size[0] - image.size[0] % self.pieces_per_side,
                image.size[1] - image.size[0] % self.pieces_per_side,
            )
        )
        self.output_size = image.size
        self.puzzle_scale = (
            image.size[0] // self.pieces_per_side,
            image.size[1] // self.pieces_per_side,
        )
        pieces = [None] * self.total_pieces
        for y in range(self.pieces_per_side):
            for x in range(self.pieces_per_side):
                pieces[y * self.pieces_per_side + x] = np.array(
                    image.crop(
                        (
                            x * self.puzzle_scale[0],
                            y * self.puzzle_scale[1],
                            (x + 1) * self.puzzle_scale[0],
                            (y + 1) * self.puzzle_scale[1],
                        )
                    )
                )
        return_pieces = [
            PuzzlePiece(piece, index_relative, self)
            for index_relative, piece in enumerate(pieces)
        ]
        return image, np.array(image).shape, return_pieces

    def get_tile_index_from_pos(self, mouse_pos: tuple[int, int]):
        """
        get_tile_index_from_pos(mouse_position):

            Uses puzzle_pos and mouse_position to determine which puzzle piece the
            mouse is currently over.
            Returns the orderlist index of the tile
        """
        mouse_x, mouse_y = mouse_pos[0] - self.puzzle_x, mouse_pos[1] - self.puzzle_y
        if (
            mouse_x < 0
            or mouse_y < 0
            or mouse_x > self.output_size[0]
            or mouse_y > self.output_size[1]
        ):
            return None
        tile_index = (
            mouse_y // self.puzzle_scale[1] * self.pieces_per_side
            + mouse_x // self.puzzle_scale[0]
        )
        return tile_index

    def get_tile_from_pos(self, mouse_pos: tuple[int, int]):
        """
        get_tile_from_pos(mouse_position):

            Calls get_tile_index_from_pos(mouse_position)
            returns the pieces index of the tile, which can be used to access the
            tile through pieces[index]
        """
        tile_index = self.get_tile_index_from_pos(mouse_pos)
        if tile_index is None:
            return None
        return self.orderlist[tile_index]

    def generate_orderlist(self, origin_tile: int = 0):
        """
        generate_orderlist():

            re-creates the orderlist from the relative_x and relative_y values of
            every PuzzlePiece
            it is a good idea to call this before using image_update()
        """
        for i in self.pieces:
            i.relative_index = i.relative_y * self.pieces_per_side + i.relative_x
            self.orderlist[i.relative_index] = i.absolute_index

    def image_update(self):
        """
        image_update():

            updates the puzzle image to reflect the order in orderlist.
            This should be called at the end of every loop where
            the puzzle is changed
        """
        temp_array = [
            np.concatenate(tuple([self.pieces[i].image for i in j]), axis=1)
            for j in [
                self.orderlist[
                    row * self.pieces_per_side : (row + 1) * self.pieces_per_side
                ]
                for row in range(self.pieces_per_side)
            ]
        ]
        self.image = make_2d_surface_from_array(
            np.concatenate(tuple(temp_array), axis=0)
        )
        EventHandler.add(EventTypes.PUZZLE_SPRITE_UPDATE)


class PuzzlePiece:
    """This is a class to store puzzle pieces and the data for them"""

    def __init__(self, image: PIL.Image.Image, relative_index: int, master: Puzzle):
        self.image = image
        self.master = master
        self.relative_index = relative_index
        self.absolute_index = relative_index
        self.relative_y, self.relative_x = divmod(
            relative_index, master.pieces_per_side
        )
        self.x = self.relative_x * master.puzzle_scale[0]
        self.y = self.relative_y * master.puzzle_scale[1]
