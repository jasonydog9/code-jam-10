import pathlib
from typing import Sequence

import numpy as np
import numpy.typing as npt
import PIL.Image
import pygame

from helpers import make_2d_surface_from_array


class MapSlicer:
    """Helper class for slicing into an image array"""

    def __init__(
        self,
        start_pos: npt.NDArray[np.int_],
        tiles_in_slice: npt.NDArray[np.int_],
        tile_pixel_size: npt.NDArray[np.int_],
    ):
        self._slice_start = start_pos
        self._slice_size = tiles_in_slice
        self._slice_multi = tile_pixel_size

    def shift(self, shift_amount: tuple[int, int] | Sequence[int]):
        """Shift slicing window in-place"""
        self._slice_start += shift_amount

    def get_slices(self, reverse: bool = True) -> tuple[slice, slice]:
        """Get tuple[x slice, y slice] for use in slicing

        Args:
            reverse: True by default, will give y, x slices instead of x, y
        """
        start = self._slice_start * self._slice_multi
        end = (self._slice_start + self._slice_size) * self._slice_multi

        # Done like this since type checker complains if a comprehension is used
        if reverse:
            return (slice(start[1], end[1]), slice(start[0], end[0]))
        else:
            return (slice(start[0], end[0]), slice(start[1], end[1]))


class GameMap:
    """Class for handling the game's map

    Args:
        floor_image_path: Path to the image to be used as the floor texture
        deco_image_path: Path to the image to be used as the decoration
        pixels_per_tile: How many pixels per floor tile
        tiles_on_screen: How many tiles fit on screen
        scaling_factor: Scale by which the image sizes will be increased
        starting_position: Offset to start the map at
    """

    def __init__(
        self,
        floor_image_path: pathlib.Path,
        deco_image_path: pathlib.Path,
        pixels_per_tile: npt.NDArray[np.int_],
        tiles_on_screen: npt.NDArray[np.int_],
        scaling_factor: int,
        starting_position: npt.NDArray[np.int_],
    ):
        self._floor_image_array = np.array(PIL.Image.open(floor_image_path))
        self._deco_image_array = np.array(PIL.Image.open(deco_image_path))
        self._map_position = MapSlicer(
            starting_position, tiles_on_screen, pixels_per_tile
        )
        self._scaling_factor = scaling_factor
        self.floor_surface: pygame.Surface = pygame.Surface((0, 0))
        self.deco_surface: pygame.Surface = pygame.Surface((0, 0))

    def update(self, shift_amount: tuple[int, int] | Sequence[int]):
        """Update the map

        Args:
            shift_amount: (x, y) amount to shift the map
        """
        self._map_position.shift(shift_amount)
        map_slices = self._map_position.get_slices()
        if all(map_slice.start >= 0 for map_slice in map_slices):
            floor_array = self._floor_image_array[map_slices[0], map_slices[1]]
            deco_array = self._deco_image_array[map_slices[0], map_slices[1]]
        else:
            array_size = np.array(
                [map_slice.stop - map_slice.start for map_slice in map_slices]
            )
            tuple_slices = np.array(
                [(map_slice.start, map_slice.stop) for map_slice in map_slices]
            )
            zero_overwrite_slices = np.zeros((2, 2), int)
            alt_array_slices = np.zeros((2, 2), int)
            for index, tup_slice in enumerate(tuple_slices):
                if tup_slice[0] < 0:
                    zero_overwrite_slices[index] = [
                        -1 * tup_slice[0],
                        array_size[index],
                    ]
                    alt_array_slices[index] = [0, tup_slice[1]]
                else:
                    zero_overwrite_slices[index] = [0, array_size[index]]
                    alt_array_slices[index] = tup_slice
            alt_slices = [slice(x, y) for x, y in alt_array_slices]
            floor_array = np.zeros([*array_size, self._floor_image_array.shape[2]], int)
            deco_array = np.zeros([*array_size, self._deco_image_array.shape[2]], int)
            if map_slices[0].start < 0 <= map_slices[1].start:
                zero_overwrite_slices[1, 1] = np.minimum(
                    zero_overwrite_slices[1, 1],
                    self._floor_image_array[alt_slices[0], alt_slices[1]].shape[1],
                )
            if map_slices[1].start < 0 <= map_slices[0].start:
                zero_overwrite_slices[0, 1] = np.minimum(
                    zero_overwrite_slices[0, 1],
                    self._floor_image_array[alt_slices[0], alt_slices[1]].shape[0],
                )
            zero_slices = [slice(x, y) for x, y in zero_overwrite_slices]
            floor_array[zero_slices[0], zero_slices[1]] = self._floor_image_array[
                alt_slices[0], alt_slices[1]
            ]
            deco_array[zero_slices[0], zero_slices[1]] = self._deco_image_array[
                alt_slices[0], alt_slices[1]
            ]

        self.floor_surface = make_2d_surface_from_array(
            floor_array,
            scaling_factor=self._scaling_factor,
        )
        self.deco_surface = make_2d_surface_from_array(
            deco_array,
            scaling_factor=self._scaling_factor,
            color_key=(255, 0, 255),
        )
