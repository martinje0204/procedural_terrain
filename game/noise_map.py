import matplotlib.pyplot as plt
from perlin_noise import PerlinNoise
import pygame
import random

class NoiseMap:
    def __init__(self, seed):
        self.seed = seed
        self.noise = PerlinNoise(octaves=8, seed=self.seed)
        self.chunk_size = 32  # tiles

    def __random_seed__(self):
        seed_length = 5
        lower_bound = 10**(seed_length-1)
        upper_bound = (10**seed_length)

        return random.randint(lower_bound,upper_bound)
    
    def new_seed(self):
        self.seed = self.__random_seed__()
        print(self.seed)
        self.noise = PerlinNoise(octaves=8, seed=self.seed)
    

    def generate_chunk(self, chunk_x, chunk_y):
        data = []
        for y in range(self.chunk_size):
            row = []
            for x in range(self.chunk_size):

                world_x = chunk_x * self.chunk_size + x
                world_y = chunk_y * self.chunk_size + y

                # sample perlin
                n = self.noise([world_x / 100, world_y / 100])
                row.append(n)

            data.append(row)

        return data   # <-- IMPORTANT
    
def draw_chunk(screen, chunk_data, chunk_x, chunk_y, camera_x, camera_y, zoom, base_tile_size=32):
    tile_size = base_tile_size * zoom

    for y, row in enumerate(chunk_data):
        for x, value in enumerate(row):

            color_value = int((value + 1) * 128)

            world_px = (chunk_x * len(chunk_data) + x) * tile_size
            world_py = (chunk_y * len(chunk_data) + y) * tile_size

            pygame.draw.rect(
                screen,
                (color_value, color_value, color_value),
                (
                    world_px - camera_x * zoom,
                    world_py - camera_y * zoom,
                    tile_size,
                    tile_size
                )
            )