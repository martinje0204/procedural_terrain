import pygame
from perlin_noise import PerlinNoise

TILE_SIZE = 32

class TileSet:
    '''
    Loads a horizontal tileset: snow, mouintain, tree, grass, sand, water.
    '''
    def __init__(self, filename):
        image = pygame.image.load(filename).convert_alpha()
        self.tiles = []

        # Automatically extract 6 tiles of TILE_SIZE width
        for i in range(6):
            rect = pygame.Rect(i * TILE_SIZE, 0, TILE_SIZE, TILE_SIZE)
            self.tiles.append(image.subsurface(rect))

    def get(self, tile_id):
        return self.tiles[tile_id]
    


class ChunkGenerator:
    '''
    Convert perlin chunk data (floats) → discrete tile IDs (0,1,2).
    '''
    def __init__(self):
        pass

    def classify(self, chunk_data):
        '''
        chunk_data: 2D list of floats in [-1,1]
        returns: same size 2D list of tile IDs in {0,1,2}
        '''
        classified = []
        for row in chunk_data:
            new_row = []
            for v in row:
                # map noise [-1, 1] into tile types
                if v < -0.2:
                    new_row.append(5)  # water
                elif v < -0.15:
                    new_row.append(4)  # sand
                elif v < 0.2:
                    new_row.append(3)  # grass
                #elif v < 0.25:
                #    new_row.append(2)  # forest
                elif v < 0.5:
                    new_row.append(1)  # mountain
                else:
                    new_row.append(0)  # snow

            classified.append(new_row)

        return classified


class ChunkRenderer:
    '''
    Builds and caches pygame.Surface objects for individual chunks.
    '''
    def __init__(self, tileset, chunk_size):
        self.tileset = tileset
        self.chunk_size = chunk_size
        self.cache = {}  # (cx, cy) → surface

    def build_surface(self, tile_ids):
        '''
        tile_ids: 2D list (chunk_size x chunk_size) of tile indices.
        '''
        surface_size = self.chunk_size * TILE_SIZE
        surf = pygame.Surface((surface_size, surface_size), pygame.SRCALPHA)

        for y, row in enumerate(tile_ids):
            for x, tile_id in enumerate(row):
                tile_img = self.tileset.get(tile_id)
                surf.blit(tile_img, (x * TILE_SIZE, y * TILE_SIZE))

        return surf

    def get_surface(self, cx, cy, tile_ids):
        '''
        Build if needed, else return cached.
        '''
        key = (cx, cy)
        if key not in self.cache:
            self.cache[key] = self.build_surface(tile_ids)
        return self.cache[key]

    def clear(self):
        # Clear all cached chunk surfaces.
        self.cache.clear()