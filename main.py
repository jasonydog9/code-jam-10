import pathlib
from types import SimpleNamespace

import numpy as np
import PIL.Image
import pygame

from GameMap.game_map import GameMap
from helpers import EventHandler, EventTypes
from Player.player import Player
from Puzzles.connector_puzzle import Connector
from Puzzles.flipping_puzzle import FlippingPuzzle
from Puzzles.lights_out_puzzle import LightsOut
from Puzzles.sliding_puzzle import SlidingPuzzle


def switch_puzzle(puzzle_index, puzzle_list: list):
    """Changes the active puzzle"""
    my_image = PIL.Image.open(puzzle_list[puzzle_index][1])
    my_pieces = puzzle_list[puzzle_index][2]
    my_puzzle = puzzle_list[puzzle_index][0](my_image, my_pieces, (380, 500))
    return my_puzzle


if __name__ == "__main__":
    directory = (pathlib.Path(__file__) / "..").resolve()
    current_puzzle = 0
    puzzles = [
        (FlippingPuzzle, directory / "sample_images/Monalisa.png", 4),
        (SlidingPuzzle, directory / "sample_images/Monalisa.png", 4),
        (LightsOut, directory / "sample_images/Monalisa.png", 4),
        # NOTE: the sample image is not used (it could be... w/ filters?)
        (Connector, directory / "sample_images/Monalisa.png", 8),
    ]

    screen = pygame.display.set_mode(
        (0, 0), pygame.FULLSCREEN
    )  # Start PyGame initialization.
    screen_size = np.array(screen.get_size())
    screen.set_colorkey((254, 0, 254))
    # This is required in order to convert PIL images into PyGame Surfaces
    pygame.init()

    running = True

    screen.fill((255, 0, 0))
    # active_puzzle = switch_puzzle(current_puzzle, puzzles)
    # screen.blit(active_puzzle.image, (0, 0))
    tile_pixel_size = np.array((16, 12))
    scaling_factor = 4
    fitting_tile_amount = np.ceil(
        np.array(screen_size) / (tile_pixel_size * scaling_factor)
    ).astype(int)
    middle_tile_pixel_location = np.array(
        (fitting_tile_amount // 2) * tile_pixel_size * scaling_factor
    )
    # offset to get the player in the middle of the tiles
    middle_tile_pixel_location += tile_pixel_size // 2
    starting_offset = np.array((2, 10))
    game_map = GameMap(
        directory / "GameMap/floor_surface.png",
        directory / "GameMap/deco_surface.png",
        tile_pixel_size,
        fitting_tile_amount,
        scaling_factor,
        starting_offset,
    )
    magic_player_offset = (fitting_tile_amount) // 2 + (0, 1)
    player = Player(scaling_factor, starting_offset + magic_player_offset)
    game_map.update((0, 0))
    screen.blit(game_map.floor_surface, (0, 0))
    screen.blit(game_map.deco_surface, (0, 0))
    screen.blit(player.image, tuple(middle_tile_pixel_location))
    EventHandler.get()

    internal_state = SimpleNamespace(in_interaction=False, current_interaction=None)

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False
            if not internal_state.in_interaction:
                player.loop(event)
            # else:
            #     active_puzzle.loop(event)

        for game_event in EventHandler.get():
            if game_event.type == EventTypes.MAP_POSITION_UPDATE:
                screen.fill((0, 0, 0))
                game_map.update(game_event.data)
                screen.blit(game_map.floor_surface, (0, 0))
                if player.z_layer:
                    screen.blit(player.image, tuple(middle_tile_pixel_location))
                    screen.blit(game_map.deco_surface, (0, 0))
                else:
                    screen.blit(game_map.deco_surface, (0, 0))
                    screen.blit(player.image, tuple(middle_tile_pixel_location))
            if game_event.type == EventTypes.PLAYER_SPRITE_UPDATE:
                screen.blit(player.image, tuple(middle_tile_pixel_location))
            if game_event.type == EventTypes.INTERACTION_EVENT:
                print(game_event.data)
            if game_event.type == EventTypes.EXIT_INTERACTION:
                internal_state.in_interaction = False
            #     if game_event == PlayerEvents.SPRITE_UPDATE:
            #         screen.blit(player.image, (0, 0))
            # if game_event.type == EventTypes.PUZZLE_SPRITE_UPDATE:
            #     screen.blit(active_puzzle.image, (0, 0))
            # if game_event.type == EventTypes.PUZZLE_SOLVED:
            #     current_puzzle += 1
            #     active_puzzle = switch_puzzle(current_puzzle, puzzles)

        pygame.display.flip()
