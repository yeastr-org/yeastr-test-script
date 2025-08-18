import match_game

match_game.test_mapping()

def inputs():
    yield 'pick PC up'
    yield 'press Q'

    yield 'go east'
    yield 'look'
    yield 'get Bed'
    yield 'look'
    yield 'get PC'
    yield 'look'
    yield 'press s'
    yield 'drop PC Bed'
    yield 'press s'
    yield 'north'
    yield 'pick up Mirror'

    yield 'get PC'
    yield 'click 50 100'
    yield 'press s'
    yield 'pick up Bed'
    yield 'press s'
    yield 'quit'

inputs = inputs()
match_game.input = lambda _: next(inputs)

exec(compile(match_game.play._source, 'match_game_play.py', 'exec'), match_game.__dict__)
match_game.play()
print('GAME OVER')
match_game.play()
print('GAME OVER')
match_game.play()
print('GAME OVER')
