import numpy as np
import pygame
import PIL
import random

'''
Parent class Puzzle
    Description:
        All image puzzles are a subset of this class.
        This class splits a puzzle image up into individual pieces that can be modified, moved, and deleted.
        It is generally assumed that the puzzle is square, so rectangular puzzles will have rectangular pieces.

    Inputs:

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

    Methods:

        modify_image(image, output_size)
            Resizes the input image to the output size.
            Splits the image into total_pieces parts, then creates a PuzzlePiece object from the image.
            PuzzlePiece object is stored in a list called pieces.
            Raises an Exception if the resized image cannot be divided into total_pieces without remainder.

        get_tile_index_from_pos(mouse_position):
            Uses puzzle_pos and mouse_position to determine which puzzle piece the mouse is currently over.
            Returns the orderlist index of the tile

        get_tile_from_pos(mouse_position):
            Calls get_tile_index_from_pos(mouse_position)
            returns the pieces index of the tile, which can be used to access the tile through pieces[index]

        generate_orderlist():
            re-creates the orderlist from the relative_x and relative_y values of every PuzzlePiece
            it is a good idea to call this before using image_update()

        image_update():
            updates the puzzle image to reflect the order in orderlist. This should be called
            at the end of every loop where the puzzle is changed

    Attributes:

    pieces_per_side:
        This is the number of pieces on any given section of the puzzle ( see below )
        if pieces_per_side is 5:
            puzzle looks like:
                   r * * * * * 
                   | * * * * * 
           5 pieces| * * * * *
                   | * * * * *
                   L * * * * *
        and total_pieces is 25.

    image:
        this is how the puzzle currently looks. On initialization, the puzzle looks like the input image.

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
'''


class Puzzle:
    def __init__(self, image, pieces_per_side, output_size, puzzle_pos):
        if type(image) is not PIL.PngImagePlugin.PngImageFile:
            raise (TypeError("Expected type " + str(PIL.PngImagePlugin.PngImageFile) + ", got type " + str(
                type(image)) + " instead."))
        self.output_size = output_size
        self.pieces_per_side = pieces_per_side
        self.total_pieces = pieces_per_side ** 2
        self.image, self.shape, self.pieces = self.modify_image(image, output_size)
        self.orderlist = list(range(0, self.total_pieces))
        self.puzzle_x, self.puzzle_y = puzzle_pos

    def modify_image(self, image, output_size):
        if output_size:
            image = image.resize(output_size)
        image = image.resize((image.size[0] - image.size[0] % self.pieces_per_side,
                              image.size[1] - image.size[0] % self.pieces_per_side))
        self.output_size = image.size
        self.puzzle_scale = (image.size[0] // self.pieces_per_side, image.size[1] // self.pieces_per_side)
        pieces = [None] * self.total_pieces
        for y in range(self.pieces_per_side):
            for x in range(self.pieces_per_side):
                pieces[y * self.pieces_per_side + x] = np.array(image.crop((
                    x * self.puzzle_scale[0],
                    y * self.puzzle_scale[1],
                    (x + 1) * self.puzzle_scale[0],
                    (y + 1) * self.puzzle_scale[1]
                )))
        return_pieces = [PuzzlePiece(piece, index_relative, self) for index_relative, piece in
                         enumerate(pieces)]
        return image, np.array(image).shape, return_pieces

    def get_tile_index_from_pos(self, mouse_pos):
        mouse_x, mouse_y = mouse_pos[0] - self.puzzle_x, mouse_pos[1] - self.puzzle_y
        if mouse_x < 0 or mouse_y < 0 or mouse_x > self.output_size[0] or mouse_y > self.output_size[1]:
            return None
        tile_index = mouse_y // self.puzzle_scale[1] * self.pieces_per_side + mouse_x // self.puzzle_scale[0]
        return tile_index

    def get_tile_from_pos(self, mouse_pos):
        tile_index = self.get_tile_index_from_pos(mouse_pos)
        if tile_index is None:
            return None
        return self.orderlist[tile_index]

    def generate_orderlist(self):
        for i in self.pieces:
            i.relative_index = i.relative_y * self.pieces_per_side + i.relative_x
            self.orderlist[i.relative_index] = i.absolute_index

    def image_update(self):
        temp_array = [np.concatenate(
            tuple([self.pieces[i].image for i in j]), axis=1) for j in
            [self.orderlist[row * self.pieces_per_side:(row + 1) * self.pieces_per_side] for row
             in range(self.pieces_per_side)]]
        self.image = pygame.surfarray.make_surface(np.swapaxes(np.concatenate(tuple(temp_array), axis=0), 0, 1))


class SlidingPuzzle(Puzzle):
    UP = (0, -1)
    DOWN = (0, 1)
    LEFT = (-1, 0)
    RIGHT = (1, 0)
    NO_MOVE = (0, 0)
    UPDATE = 0
    SOLVED = 1

    def __init__(self, image, pieces_per_side, output_size=(), puzzle_pos=(0, 0)):
        super().__init__(image, pieces_per_side, output_size, puzzle_pos)
        self.scramble()
        self.image_update()
        self.event = []

    def scramble(self):
        self.orderlist.pop()
        self.last_piece = self.pieces.pop()
        self.last_image = self.last_piece.image
        self.last_piece.image = np.full(self.pieces[0].image.shape, fill_value=0, dtype=np.uint8)
        temp_list = self.orderlist.copy()
        while temp_list == self.orderlist:
            random.shuffle(self.orderlist)
            if not self.solvable(self.orderlist):
                self.orderlist[-1], self.orderlist[-2] = self.orderlist[-2], self.orderlist[-1]
        self.orderlist.append(self.total_pieces - 1)
        self.pieces.append(self.last_piece)
        for pos, i in enumerate(self.orderlist):
            self.pieces[i].relative_y, self.pieces[i].relative_x = divmod(pos, self.pieces_per_side)

    def loop(self, event):
        if event.type == pygame.MOUSEBUTTONUP:
            mouse_start = pygame.mouse.get_pos()
            temp = self.get_tile_index_from_pos(mouse_start)
            if temp is not None:
                self.move(self.tile_can_move(temp))
                self.event.append(SlidingPuzzle.UPDATE)

    def tile_can_move(self, tile_index):
        # Get tiles in row
        orderlist_index_start = tile_index // self.pieces_per_side * self.pieces_per_side
        orderlist_index_end = tile_index // self.pieces_per_side * self.pieces_per_side + self.pieces_per_side
        column_number = tile_index % self.pieces_per_side
        orderlist_column = [self.orderlist[column_number + i * self.pieces_per_side] for i in
                            range(self.pieces_per_side)]
        orderlist_row = self.orderlist[orderlist_index_start:orderlist_index_end]
        if self.total_pieces - 1 in orderlist_column:
            zero_index = orderlist_column.index(self.total_pieces - 1)
            tile_index_relative = tile_index // self.pieces_per_side
            delta = zero_index - tile_index_relative
            if delta == 0:
                return SlidingPuzzle.NO_MOVE, [], tile_index
            direction = SlidingPuzzle.UP if delta < 0 else SlidingPuzzle.DOWN
            indices = [column_number + i * self.pieces_per_side for i in range(self.pieces_per_side)]
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

        movable = [indices[i] for i in
                   range(tile_index_relative, zero_index, [i for i in direction if i != 0][0])]
        return direction, movable, tile_index

    def move(self, direction_tile_list_origin_tile):
        direction, tile_list, origin_tile = direction_tile_list_origin_tile
        if direction == SlidingPuzzle.NO_MOVE:
            return 0
        for i in tile_list:
            self.pieces[self.orderlist[i]].relative_x += direction[0]
            self.pieces[self.orderlist[i]].relative_y += direction[1]
        self.generate_orderlist(origin_tile)
        self.image_update()
        if self.orderlist == list(range(self.total_pieces)):
            self.event.append(SlidingPuzzle.SOLVED)

    def generate_orderlist(self, origin_tile):
        for i in self.pieces:
            if i.absolute_index == self.total_pieces - 1:
                i.relative_y = origin_tile // self.pieces_per_side
                i.relative_x = origin_tile % self.pieces_per_side
                i.relative_index = origin_tile
                continue

            i.relative_index = i.relative_y * self.pieces_per_side + i.relative_x
            self.orderlist[i.relative_index] = i.absolute_index
        self.orderlist[origin_tile] = self.total_pieces - 1

    def solvable(self, unsorted):
        inversions = 0
        for j in range(self.total_pieces - 1):
            for i in range(j + 1, self.total_pieces - 1):
                if unsorted[j] > unsorted[i]:
                    inversions += 1
        return inversions % 2 == 0


class ExamplePuzzle(Puzzle):

    def __init__(self, image, pieces_per_side, output_size=(), puzzle_pos=(0, 0)):
        super().__init__(image, pieces_per_side, output_size, puzzle_pos)
        self.scramble()
        self.generate_orderlist()
        self.image_update()

    def loop(self):
        # put code here to be run every frame, such as an event loop
        pass

    def scramble(self):
        # put the code to scramble your image here
        pass


class PuzzlePiece:

    def __init__(self, image, relative_index, master):
        self.image = image
        self.master = master
        self.relative_index = relative_index
        self.absolute_index = relative_index
        self.relative_y, self.relative_x = divmod(relative_index, master.pieces_per_side)
        self.x = self.relative_x * master.puzzle_scale[0]
        self.y = self.relative_y * master.puzzle_scale[1]
