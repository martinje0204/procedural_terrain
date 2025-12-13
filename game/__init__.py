import pygame
import sys
import random
from perlin_noise import PerlinNoise
from .terrain import ChunkRenderer, ChunkGenerator, TileSet
from pathlib import Path

TILE_SIZE = 32  # base tile size in pixels
tilesheet_path = Path(__file__).parent / 'assets' / 'tilesheet.png'
logo_path = Path(__file__).parent / 'assets' / 'maryland_ball.png' 


class Game:
    def __init__(self):
        pygame.init()
        pygame.font.init()
        self.font = pygame.font.SysFont(None, 24)

        # set up game display
        self.info = pygame.display.Info()

        # take user screen size and make window half that size
        self.screen_width = self.info.current_w * 0.5
        self.screen_height = self.info.current_h * 0.5
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height), pygame.RESIZABLE)
        self.bg_color = pygame.Color('black')
    
        pygame.display.set_caption("Perlin Noise Terrain Demo")
        logo = pygame.image.load(logo_path) 
        pygame.display.set_icon(logo) # when I learned I could do this I had to put a custom icon

        # initialize terrain noise
        self.seed = 18257  # initialize with any integer seed, can be changed during runtime
        self.noise = NoiseMap(seed=self.seed, chunk_size=32, octaves=6)

        self.clock = pygame.time.Clock()

        # initialize terrain components
        self.tileset = TileSet(tilesheet_path)
        self.classifier = ChunkGenerator() # makes matrix of integer tile IDs from perlin noise values
        self.chunk_renderer = ChunkRenderer(self.tileset, self.noise.chunk_size)
        self.loaded_chunks = {}
        self.chunk_radius = 1

        # initialize camera
        self.camera = Camera(self.screen_width, self.screen_height)
        self.camera.x = 0.0
        self.camera.y = 0.0

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    self.__reset_chunks__()
                if event.key == pygame.K_e:
                    self.camera.zoom_in()
                if event.key == pygame.K_q:
                    self.camera.zoom_out()

    def update(self):
        pressed_keys = pygame.key.get_pressed()
        move_speed = 10
        if pressed_keys[pygame.K_w]:
            self.camera.move(0, -move_speed)
        if pressed_keys[pygame.K_s]:
            self.camera.move(0, move_speed)
        if pressed_keys[pygame.K_a]:
            self.camera.move(-move_speed, 0)
        if pressed_keys[pygame.K_d]:
            self.camera.move(move_speed, 0)

        # preload chunks around current view
        self.preload_chunks()

    def draw(self):
        self.screen.fill(self.bg_color)

        chunk_tile_size = self.noise.chunk_size  # tiles per chunk (e.g. 32)
        base_chunk_px = chunk_tile_size * TILE_SIZE  # px per chunk at zoom=1

        # find visible chunk range from camera
        min_cx, max_cx, min_cy, max_cy = self.camera.get_visible_chunk_range(chunk_tile_size)

        # create a margin to draw extra chunks around the camera's view
        min_cx -= self.chunk_radius
        max_cx += self.chunk_radius
        min_cy -= self.chunk_radius
        max_cy += self.chunk_radius
    
        for cy in range(min_cy, max_cy + 1):
            for cx in range(min_cx, max_cx + 1):

                # Only draw if the chunk has already been loaded
                if (cx, cy) in self.loaded_chunks:
                    surface = self.loaded_chunks[(cx, cy)]

                    world_x = cx * base_chunk_px
                    world_y = cy * base_chunk_px

                    screen_x = (world_x - self.camera.x) * self.camera.zoom
                    screen_y = (world_y - self.camera.y) * self.camera.zoom

                    scaled = pygame.transform.scale(
                        surface,
                        (int(surface.get_width() * self.camera.zoom),
                        int(surface.get_height() * self.camera.zoom))
                    )

                    self.screen.blit(scaled, (screen_x, screen_y))
    
        self.clock.tick(60)
        text_surface = self.font.render('Press WASD to move. Press Q/E to zoom. Press R to load new seed.', True, (0, 0, 0)) # Black text
        text_rect = text_surface.get_rect(center=(self.screen_width // 2, 12))
        self.screen.blit(text_surface, text_rect)
        pygame.display.flip()

    def get_chunk(self, cx, cy):
        # take chunk coordinates, return the chunk surface, either from cache or generate it if needed
        if (cx, cy) not in self.loaded_chunks:
            raw = self.noise.generate_chunk(cx, cy)
            tiles = self.classifier.classify(raw)
            surface = self.chunk_renderer.get_surface(cx, cy, tiles)
            self.loaded_chunks[(cx, cy)] = surface
        return self.loaded_chunks[(cx, cy)]
    
    def preload_chunks(self):\

        chunk_tile_size = self.noise.chunk_size
        min_cx, max_cx, min_cy, max_cy = self.camera.get_visible_chunk_range(chunk_tile_size)

        min_cx -= self.chunk_radius
        max_cx += self.chunk_radius
        min_cy -= self.chunk_radius
        max_cy += self.chunk_radius

        for cy in range(min_cy, max_cy + 1):
            for cx in range(min_cx, max_cx + 1):
                if (cx, cy) not in self.loaded_chunks:
                    # generate one chunk per update to avoid stutter
                    raw = self.noise.generate_chunk(cx, cy)
                    tiles = self.classifier.classify(raw)
                    surface = self.chunk_renderer.get_surface(cx, cy, tiles)
                    self.loaded_chunks[(cx, cy)] = surface
                    return 
                
    def __reset_chunks__(self):
        # Clear cached chunks so they'll regenerate (used on 'r' key)
        self.loaded_chunks.clear()
        self.noise.new_seed()
        self.chunk_renderer.clear() 

                
            
class NoiseMap:
    '''
    Perlin noise chunk generator. Returns a 2D array of floats in [-1,1].
    '''
    def __init__(self, seed=None, chunk_size=32, octaves=6):
        self.seed = seed if seed is not None else self._random_seed()
        self.chunk_size = chunk_size  # tiles per chunk
        self.octaves = octaves
        self._recreate_noise()

    def _random_seed(self, seed_length=5):
        lower_bound = 10 ** (seed_length - 1)
        upper_bound = 10 ** seed_length - 1
        return random.randint(lower_bound, upper_bound)

    def _recreate_noise(self):
        self.noise = PerlinNoise(octaves=self.octaves, seed=self.seed)

    def new_seed(self):
        self.seed = self._random_seed()
        print(f"New seed:  {self.seed}")
        self._recreate_noise()

    def generate_chunk(self, cx, cy, scale=200.0): # scale = changes resolution of terrain, higher = smoother terrain generation
        # Return chunk_size x chunk_size list of float noise values [-1,1]
        data = []
        for y in range(self.chunk_size):
            row = []
            for x in range(self.chunk_size):
                world_x = cx * self.chunk_size + x
                world_y = cy * self.chunk_size + y
                n = self.noise([world_x / scale, world_y / scale])
                row.append(n)
            data.append(row)
        return data


class Camera:
    '''
    Camera holds a top-left world position in pixels and a zoom factor.
    '''
    def __init__(self, width, height):
        self.x = 0.0  # world pixel coordinates (top-left of the view)
        self.y = 0.0
        self.width = width
        self.height = height
        self.zoom = 1
        self.min_zoom = 0.25
        self.max_zoom = 20

    def move(self, dx, dy):
        # dx, dy are in screen pixels; convert to world-space movement
        self.x += dx * (1 / self.zoom)
        self.y += dy * (1 / self.zoom)

    def zoom_in(self, factor=1.1):
        old = self.zoom
        self.zoom = min(self.zoom * factor, self.max_zoom)
        return old, self.zoom

    def zoom_out(self, factor=1.1):
        old = self.zoom
        self.zoom = max(self.zoom / factor, self.min_zoom)
        return old, self.zoom

    def get_visible_chunk_range(self, chunk_tile_size):
        '''
        Return min_chunk_x, max_chunk_x, min_chunk_y, max_chunk_y
        based on camera position and current zoom. chunk_tile_size is tiles per chunk.
        '''
        chunk_px_size = chunk_tile_size * TILE_SIZE  # pixels per chunk

        # view rect in world pixels (top-left origin)
        view_left = self.x
        view_top = self.y
        view_right = self.x + (self.width / self.zoom)
        view_bottom = self.y + (self.height / self.zoom)

        min_chunk_x = int(view_left // chunk_px_size) - 1
        min_chunk_y = int(view_top // chunk_px_size) - 1
        max_chunk_x = int(view_right // chunk_px_size) + 1
        max_chunk_y = int(view_bottom // chunk_px_size) + 1

        return min_chunk_x, max_chunk_x, min_chunk_y, max_chunk_y

