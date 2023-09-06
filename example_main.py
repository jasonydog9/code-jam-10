from PIL import Image
import pygame
import Puzzle

PIECES_PER_SIDE = 3

'''
Get puzzle image and data.
'''
puzzle_image = Image.open('code-jam-10/sample_images/Monalisa.png')

'''
Start PyGame initialization. This is required in order to convert PIL images into PyGame Surfaces
'''
screen = pygame.display.set_mode((380, 500))
pygame.init()

'''
Create new puzzle object given puzzle pieces
'''
sliding_puzzle = Puzzle.SlidingPuzzle(puzzle_image, PIECES_PER_SIDE, (380, 500))

running = True
mouse_held = False
mouse_was_held = False
screen.fill((255, 0, 0))
screen.blit(sliding_puzzle.image, (0, 0))
while running:

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        sliding_puzzle.loop(event)

    if sliding_puzzle.UPDATE in sliding_puzzle.event:
        screen.blit(sliding_puzzle.image, (0, 0))
        sliding_puzzle.event.remove(Puzzle.SlidingPuzzle.UPDATE)
    pygame.display.flip()