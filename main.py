from game import Game
# boiler plate from: https://www.youtube.com/watch?v=fGSOHM4mv40
if __name__ == '__main__':
    game = Game()

    while True:
        game.handle_events()
        game.update()
        game.draw()