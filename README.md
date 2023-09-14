# The Pickled Peps

- [The Pickled Peps](#the-pickled-peps)
  - [Team Members](#team-members)
  - [Getting Stared](#getting-started)
- [Build Idea and Scope](#build-idea-and-scope)
  - [Original Scope](#original-scope)
  - [Final Scope](#final-scope)
  - [Theme Connections](#theme-connections)
  - [Technologies Used](#technologies-used)
- [The Navigable Map](#the-navigable-map)
  - [The Visible Map](#the-visible-map)
  - [The Floor Surface](#the-floor-surface)
  - [The Deco Surface](#the-deco-surface)
  - [The GameMap Class](#the-gamemap-class)
  - [Movement and the Player Class](#movement-and-the-player-class)
  - [The Collision Map](#the-collision-map)
- [The Puzzles](#the-puzzles)
  - [The Puzzle Class](#the-puzzle-class)
  - [Flipping Puzzle](#flipping-puzzle)
  - [Invert Puzzle/Lights Out](#invert-puzzlelights-out)
  - [Sliding Puzzle/15 Puzzle](#sliding-puzzle15-puzzle)
  - [Connector Puzzle/Flow Puzzle](#connector-puzzleflow-puzzle)
- [The helpers.py File](#the-helperspy-file)


## Team Members
 - A5rocks
 - at
 - BigbadSmurfface
 - GiGaGon
 - Inventor4Life

<sub>Markdown by GiGaGon based on the [Google Slides](https://docs.google.com/presentation/d/1hVHyL-425JmXZ2i5i8JCnnOdkUPW1x4VkbowvxzCYfg/)</sub>


## Getting Started

To run the game, clone the repo with `git clone <repo url>`

CD into the directory and run `python -m venv venv` to create the venv

Run `./venv/Scripts/activate` or `source venv/bin/activate` to active the venv

Run `pip install -r requirements.txt` to install the requirements

Run `python main.py` to launch the game

Basic controls are wasd/arrow keys to move, mouse to interact with puzzles


# Build Idea and Scope


## Original Scope

Have to escape a room by solving puzzles related to images and cyphers

Pixel art aesthetic, isomorphic perspective

Cyphers give you the steps that are used in constructing final “key” images from the ones fixed and gathered thought the map

![image.png.url](https://cdn.discordapp.com/attachments/1145776473337245797/1147973397347844146/image.png)

<sub>Concept game loop diagram by GiGaGon</sub>


## Final Scope

As the deadline approached:
 - Top down perspective was used as the complexity is lower than isometric
 - No cyphers were successfully implemented
 - Image puzzles never got their own locations
 - No proper menus, lacking world interactivity
 - No image combinations
 - No end screen, game crashes when all puzzles are finished

Currently implemented ideas:
 - Navigable map with partial interaction system
 - Flipping, inversion, and sliding puzzles
 - Semi-extensible framework
 - (half-hearted) Transition between map navigation and puzzle solving


## Theme Connections

Image manipulation:
 - The implemented puzzles all have to do with manipulating an image
 - The actual manipulation of the images happens only through numpy, with loading from PIL

Secret Codes:
 - Originally, the images themselves were part of the “secret code”
 - The cypher puzzles would have been a more literal interpretation of the “secret code” theme
 - The image combination steps would have tied the systems together


## Technologies Used
Image loading:
 - PIL

Image processing:
 - Numpy

Image display and input handling:
 - Pygame

Code formatting:
 - Black
 - ISort
 - Flake8

Code quality:
 - MyPy


# The Navigable Map


## The Visible Map

The visible map is split into two layers, the floor surface and the deco surface

The floor surface will always be displayed under the player character

The deco surface will either be below or above the player character, implementation details later

The visible map gets position updates from the player, and uses that to slice different sections of the surfaces, giving the illusion of movement

https://github.com/A5rocks/code-jam-10/assets/107241144/fb774664-a429-4668-8ebf-224fcd3a2e24

<sub>Game was recorded smaller than normal to better fit in the presentation</sub>


## The Floor Surface

<sub>Created by Inventor4Life and tweaked by GiGaGon</sub>

The floor surface is the always visible background layer, drawn under the player character

The floor tiles are originally 16x16, squished to 16x12 for the perspective

Due to alpha issues between Numpy arrays and pygame explained later, the shadows need to be on this image

Assets found by BigbadSmurfface, created by [ShatteredReality](https://shatteredreality.itch.io) and uploaded [here on itch.io](https://shatteredreality.itch.io/shpa) under the Creative Common Zero v1.0 Universal license

![floor_surface](https://github.com/A5rocks/code-jam-10/assets/107241144/b3222ba8-369e-46b7-83f1-92eb45682009)


## The Deco Surface

<sub>Created by Inventor4Life and tweaked by GiGaGon</sub>

The floor surface will either be below or above the player depending on the z order from the collision map. The lets the player walk behind objects

Since pygame doesn't support RGBA arrays, the deco layer uses a `(255, 0, 255)` chroma key for transparency

Assets found by BigbadSmurfface, created by [ShatteredReality](https://shatteredreality.itch.io) and uploaded [here on itch.io](https://shatteredreality.itch.io/shpa) under the Creative Common Zero v1.0 Universal license

![deco_surface](https://github.com/A5rocks/code-jam-10/assets/107241144/db9d5444-4dfe-4a78-8678-8f2c0877b4f6)


## The GameMap Class

<sub>Developed by GiGaGon</sub>

The GameMap class manages the different surfaces

It is instantiated in main, and takes in the two surface image paths along with the relevant needed info for rendering correctly

The scaling factor is used when creating the surface to scale up the pixel art to a visible size

```python
game_map = GameMap(
    directory / "GameMap/floor_surface.png",
    directory / "GameMap/deco_surface.png",
    tile_pixel_size,
    fitting_tile_amount,
    scaling_factor,
    starting_offset,
    )
```

The update method takes in a movement vector `py tuple[int, int]` that is included in the `EventTypes.MAP_POSITION_UPDATE` event, and moves the map accordingly

```python
for game_event in EventHandler.get():
    if game_event.type == EventTypes.MAP_POSITION_UPDATE:
        screen.fill((0, 0, 0))
        game_map.update(game_event.data)
```


## Movement and the Player Class

<sub>Developed by GiGaGon</sub>

Movement is done with either the arrow keys or WASD

The key alternatives, as well as the sprites are hard coded in the player.py file

```python
class MovementDirections(Enum):
    UP = (0, -1)
    DOWN = (0, 1)
    LEFT = (-1, 0)
    RIGHT = (1, 0)
    NULL = (0, 0)

KEYPRESS_ALTERNATIVES: dict[int, MovementDirections] = {
    **dict.fromkeys([pygame.K_w, pygame.K_UP], MovementDirections.UP),
    **dict.fromkeys([pygame.K_s, pygame.K_DOWN], MovementDirections.DOWN),
    **dict.fromkeys([pygame.K_a, pygame.K_LEFT], MovementDirections.LEFT),
    **dict.fromkeys([pygame.K_d, pygame.K_RIGHT], MovementDirections.RIGHT),
}

PLAYER_SPRITES: dict[MovementDirections, numpy.typing.NDArray] = {
    MovementDirections.UP: np.array(PIL.Image.open("Player/player_up.png")),
    MovementDirections.DOWN: np.array(PIL.Image.open("Player/player_down.png")),
    MovementDirections.LEFT: np.array(PIL.Image.open("Player/player_left.png")),
    MovementDirections.RIGHT: np.array(PIL.Image.open("Player/player_right.png")),
}
```

The player “moves” by updating an internal position, and being drawn to the center of the screen in the correct orientation

```python
if game_event.type == EventTypes.PLAYER_SPRITE_UPDATE:
    screen.blit(player.image, tuple(middle_tile_pixel_location))
```

If the player actually moved and didn't just rotate or stand still, this info is passed to the `GameMap` through an `EventTypes.MAP_POSITION_UPDATE` event

```python
EventHandler.add(EventTypes.MAP_POSITION_UPDATE, movement_direction.value)
```


The player class is instantiated with just the scaling factor and starting position, since the image paths were hardcoded

The final product is free from collision/visible map desyncs, but there is still the unintended behavior of the starting position changing if the window size changes

The middle tile offset is used later when blitting the player sprite

```python
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
...
magic_player_offset = (fitting_tile_amount) // 2 + (0, 1)
player = Player(scaling_factor, starting_offset + magic_player_offset)
```

Player sprites created by Inventor4Life

![player_sprites](https://github.com/A5rocks/code-jam-10/assets/107241144/244f481b-2f59-4d9e-8608-3624954bfd70)


## The Collision Map

<sub>Map by Inventor4Life and implementation by GiGaGon </sub>

Collision is handled through a colored image that is m by n pixels wide, where m and n are the amount of tiles in the displayed map

The collision map is loaded in the player.py file

```python
self._collision_map = np.array(
    PIL.Image.open("Player/collision_map.png")
).swapaxes(0, 1)
```

Due to some implementation misunderstandings, the image must be a transparent PNG and not a 24-bit PNG

Implementation:
```
 - Red       (255, 0, 0) = Solid
 - Blue      (0, 255, 0) = Walkable, Z Layer 0
 - Dark Blue (0, 127, 0) = Walkable, Z Layer 1
 - Green     (0, 0, 255) = Solid and Interactable
```

In-game collision map:

![collision_map](https://github.com/A5rocks/code-jam-10/assets/107241144/d286734a-4177-43bb-ab63-7985168f9802)

# The Puzzles


## The Puzzle Class

<sub>Developed by Inventor4Life</sub>

The base class for the rest of the puzzles

Interaction is done via the mouse

Contains methods that normally don't need overwritten and are provided for convenience

The only method that needs to be implemented in subclasses is `loop`

Subclasses are instantiated with an image directory, the number of tiles per side, and the target display size

The puzzle image paths and tile numbers are stored in a list in main

```python
current_puzzle = 0
puzzles = [
    (FlippingPuzzle, directory / "sample_images/Monalisa.png", 4),
    (SlidingPuzzle, directory / "sample_images/Monalisa.png", 4),
    (LightsOut, directory / "sample_images/Monalisa.png", 4),
    # NOTE: the sample image is not used (it could be... w/ filters?)
    (Connector, directory / "sample_images/Monalisa.png", 8),
]
```

When it is time to switch to the next puzzle (ie, on puzzle completion) a helper function is used to return the new puzzle instance

```python
def switch_puzzle(puzzle_index, puzzle_list: list):
    """Changes the active puzzle"""
    my_image = PIL.Image.open(puzzle_list[puzzle_index][1])
    my_pieces = puzzle_list[puzzle_index][2]
    my_puzzle = puzzle_list[puzzle_index][0](my_image, my_pieces, (380, 500))
    return my_puzzle
```


## Flipping Puzzle

<sub>Developed by BigbadSmurfface</sub>

An image is separated into tiles, some of which are flipped horizontally

When a tile is pressed, it flips horizontally

The goal is to return the image to a completely unflipped state

https://github.com/A5rocks/code-jam-10/assets/107241144/55ee27bb-323f-4c18-90eb-7824ef80174d


## Invert Puzzle/Lights Out

<sub>Developed by Inventor4Life</sub>

An image is separated into tiles, with some having their colors inverted

When a tile is pressed, the tile plus the 4 adjacent tiles invert in color

The goal is to return the image to a completely un-inverted state

https://github.com/A5rocks/code-jam-10/assets/107241144/8609ec18-a8ed-47e8-ab60-082a9adc1dc4


## Sliding Puzzle/15 Puzzle

<sub>Developed by Inventor4Life</sub>

An image is separated into randomly shuffled tiles, with one removed

When a tile is pressed, the empty space moves there if orthogonally adjacent

The goal is to return the image to an unshuffled state

https://github.com/A5rocks/code-jam-10/assets/107241144/907de409-06e8-480b-82bf-72867862b41b

<sub>Sped up for your convenience, the original is 3 mins long and can be found [here](https://drive.google.com/file/d/1p0afJMl0aI5bgVWNmq0VP_NZWMeff6an/view?usp=sharing)</sub>


## Connector Puzzle/Flow Puzzle

<sub>Developed by A5rocks</sub>

Generate blue, red, and green tiles in a grid of white tiles

When a tile is pressed, cycle through white -> red -> green -> blue

Right mouse button cycles the opposite direction

The goal is to connect the starting tiles through a path of the same color

Currently may not always generate a solvable puzzle

https://github.com/A5rocks/code-jam-10/assets/107241144/3f43d3e7-7786-4427-9a95-08715f09a57b


# The `helpers.py` File

<sub>Developed by GiGaGon</sub>

make_2d_surface_from_array - since pygame's default makesurface has some issues, this function attempts to solve them. It takes in a numpy array, flips it if needed (for PIL created arrays), does the upscaling, and can apply a color key

EventTypes - Simple event type enum for all the event types the program uses

```python
class EventTypes(Enum):
    PLAYER_SPRITE_UPDATE = auto()
    PLAYER_MOVEMENT_UPDATE = auto()
    PUZZLE_SPRITE_UPDATE = auto()
    PUZZLE_SOLVED = auto()
    MAP_POSITION_UPDATE = auto()
    INTERACTION_EVENT = auto()
    EXIT_INTERACTION = auto()
```

Event - a type to mimic pygame's events, store both the enum type and optional data

```python
EventHandler.add(EventTypes.MAP_POSITION_UPDATE, movement_direction.value)
```

EventHandler - a handler to mimic pygame's events, stores a list of Events, clears on read

```python
for game_event in EventHandler.get():
    if game_event.type == EventTypes.MAP_POSITION_UPDATE:
        screen.fill((0, 0, 0))
        game_map.update(game_event.data)
```
