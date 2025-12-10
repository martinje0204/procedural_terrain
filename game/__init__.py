import pygame
import sys

from .tilesheet import TileSheet
from .noise_map import NoiseMap, draw_chunk

class Game:
    def __init__(self):
        pygame.init()
        
        self.screen = pygame.display.set_mode((1280, 640))
        self.clock = pygame.time.Clock()

        self.bg_color = pygame.Color('black')

        self.tiles = TileSheet('assets/tilesheet.png', 32, 32, 1, 3)

        self.camera_x = 0
        self.camera_y = 0

        self.zoom = 1.0        # 1.0 = normal size
        self.zoom_step = 0.01   # how much zoom changes per key press

        self.speed = 5   


        self.loaded_chunks = {}
        self.chunk_radius = 2  # loads a 5×5 region around the player

        # NEW: create noise system
        self.noise = NoiseMap(seed=1337)

        # generate a test chunk
        self.chunk00 = self.noise.generate_chunk(0, 0)
        self.chunk10 = self.noise.generate_chunk(1, 0)
        self.chunk01 = self.noise.generate_chunk(0, 1)
    def __reset_chunks__(self):
        print("reset chunks")
        
        self.noise.new_seed() # get new seed


    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    self.__reset_chunks__()
    def update(self):
        pressed_keys = pygame.key.get_pressed()
        if pressed_keys[pygame.K_w]:
            self.camera_y -= self.speed
        if pressed_keys[pygame.K_s]:
            self.camera_y += self.speed
        if pressed_keys[pygame.K_a]:
            self.camera_x -= self.speed
        if pressed_keys[pygame.K_d]:
            self.camera_x += self.speed
        if pressed_keys[pygame.K_e]:
            self.zoom += self.zoom_step
            if self.zoom > 3:
                self.zoom = 3  
        if pressed_keys[pygame.K_q]:
            self.zoom -= self.zoom_step
            if self.zoom < 0.3:
                self.zoom = 0.3  
    def draw(self):
        self.screen.fill(self.bg_color)

        tile_size = 32
        chunk_size_px = self.noise.chunk_size * tile_size

        # Determine current chunk the camera is over
        current_chunk_x = self.camera_x // chunk_size_px
        current_chunk_y = self.camera_y // chunk_size_px

        # Load and draw all chunks in radius
        for dy in range(-self.chunk_radius, self.chunk_radius + 1):
            for dx in range(-self.chunk_radius, self.chunk_radius + 1):

                cx = current_chunk_x + dx
                cy = current_chunk_y + dy

                chunk = self.get_chunk(cx, cy)

                draw_chunk(
                    self.screen,
                    chunk,
                    cx, cy,
                    self.camera_x, self.camera_y,
                    self.zoom
                )

        pygame.display.flip()

    def get_chunk(self, cx, cy):
        if (cx, cy) not in self.loaded_chunks:
            self.loaded_chunks[(cx, cy)] = self.noise.generate_chunk(cx, cy)
        return self.loaded_chunks[(cx, cy)]