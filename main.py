from game import Game

'''
ENAE380 Final Project
Perlin Noise Terrain Generation with Pygame
'''

# boiler plate from: https://www.youtube.com/watch?v=fGSOHM4mv40
if __name__ == '__main__':
    game = Game()

    while True:
        game.handle_events()
        game.update()
        game.draw()