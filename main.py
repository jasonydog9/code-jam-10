import pygame
from PIL import Image

import puzzle
from lights_out_puzzle import LightsOut

# from sliding_puzzle import SlidingPuzzle

PIECES_PER_SIDE = 4

if __name__ == "__main__":
    puzzle_image = Image.open(
        "code-jam-10/sample_images/Monalisa.png"
    )  # get puzzle image and data
    screen = pygame.display.set_mode((380, 500))  # Start PyGame initialization.
    # This is required in order to convert PIL images into PyGame Surfaces
    pygame.init()
    sliding_puzzle = LightsOut(
        puzzle_image, PIECES_PER_SIDE, (380, 500)
    )  # Create new puzzle object given puzzle pieces

    running = True

    screen.fill((255, 0, 0))
    screen.blit(sliding_puzzle.image, (0, 0))

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            sliding_puzzle.loop(event)

        if puzzle.Puzzle.UPDATE in sliding_puzzle.event:
            screen.blit(sliding_puzzle.image, (0, 0))
            sliding_puzzle.event.remove(puzzle.Puzzle.UPDATE)

        pygame.display.flip()
