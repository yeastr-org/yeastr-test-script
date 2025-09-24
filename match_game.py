from yeastr.bootstrapped import *
from yeastr.as_decorator import backport_match, with_call2comp, with_namedloops
from abc import ABC, abstractmethod
from dataclasses import dataclass


@backport_match()
def test_mapping():
    actions = [
        {"text": "ok", "color": "red"},
        {"text": "<b>ok</b>", "color": "red", "style": "bold"},
        {"sleep": "1s"},
        {"sound": "file:///path.oga", "format": "ogg"},
        {"sound": "file:///path.mp9", "format": "mp9"},
        {"error": "msg", "location": (3, 4), "subsystem": "some"},
    ]
    for action in actions:
        match action:
            case {"text": message, "color": c}:
                print(f'ui.set_text_color({c})')
                print(f'ui.display({message})')
            case {"sleep": duration}:
                print(f'ui.wait({duration})')
            case {"sound": url, "format": "ogg"}:
                print(f'ui.play({url})')
            case {"sound": _, "format": _}:
                print('warning("Unsupported audio format")')
            case {"error": msg, **rest}:
                print(msg, rest)
test_mapping()

class Room(ABC):
    name = 'Room'
    #objects = []
    #directions = {}

    @with_call2comp()
    def describe(self):
        print('Room:', self.name)
        print('Objects:', ', '.join(self.objects))
        print('Directions:', ', '.join(emap(
            lambda direction, room:
                f'{direction}={room.name}',
            self.directions.items()
        )))

    @abstractmethod
    def neighbor(self, direction): ...

    @property
    def exits(self):
        return self.directions.keys()

class MainRoom(Room):
    name = 'Main'

    def neighbor(self, direction):
        return self.directions.get(direction, self)

class KitchenRoom(Room):
    name = 'Kitchen'

    def neighbor(self, direction):
        return self.directions.get(direction, self)

class MirrorsRoom(Room):
    name = 'Mirrors'

    def neighbor(self, direction):
        if direction == 'back':
            return MainRoom()
        print('You get lost and starved to death')
        raise Break('mainloop')

MainRoom.directions = {
    'est': KitchenRoom(),
    'north': MirrorsRoom(),
}
KitchenRoom.directions = {
    'west': MainRoom(),
}
MirrorsRoom.directions = {
    'back': MainRoom(),
}

def reset_rooms():
    MainRoom.objects = ['PC', 'Bed']
    MirrorsRoom.objects = ['Mirror', ]
    KitchenRoomobjects = ['Cofee', 'Moka']


class Character:
    def __init__(self):
        self.objects = []

    def get(self, obj, current_room):
        if obj in current_room.objects:
            if obj == 'Mirror':
                print('You became a narcisist, forgot to eat then died')
                raise Break('mainloop')
            current_room.objects.remove(obj)
            self.objects.append(obj)
            return obj
        print('Endless research lead to death')
        raise Break('mainloop')

    def drop(self, obj, current_room):
        if obj in self.objects:
            self.objects.remove(obj)
            current_room.objects.append(obj)
        else:
            print('You looked hard, then started to look inside your body, you\'re now dead in a pool of blood')
            raise Break('mainloop')

class Event:  # such a mock, multithreading events...
    def __init__(self):
        self.data = False
    def get(self):
        return self.data.pop() if self.data else False
    def set(self, evt):
        self.data = [evt]

class Click:
    def __init__(self, position):
        self.position = position

@dataclass
class ClickDc:
    position: tuple  # tuple[str, str]
    kind: str = 'Right'

class ClickMatchable:
    __match_args__ = ('position', 'kind')
    def __init__(self, position, kind):
        self.position = position
        self.kind = kind

class KeyPress:
    def __init__(self, kn):
        self.key_name = kn


@backport_match(custom_globals=globals(), debug=True)
@with_namedloops()
def play():
    character = Character()
    reset_rooms()
    current_room = MainRoom()
    event = Event()
    with While(True) as mainloop:
        print(f'In your pockets: {character.objects}')
        command = input('Command:')
        match command.split():
            case ["quit"]:
                print("Goodbye!")
                mainloop.Break
            case ["look"]:
                current_room.describe()
            case ["get", obj]:
                character.get(obj, current_room)
            case ["north"] | ["go", "north"]:
                current_room = current_room.neighbor("north")
            case ["go", ("north" | "south" | "east" | "west") as direction]:
                print(f'You tried to go {direction}')
                print('but nah...')
            case ["go", direction] if direction in current_room.exits:
                current_room = current_room.neighbor(direction)
            case ["go", _]:
                print("Sorry, you can't go that way")
            case ["get", obj] | ["pick", "up", obj] | ["pick", obj, "up"]:
                character.get(obj, current_room)
            case ["drop", *objects, 'Hearth']:
                print('You don\'t have one, died')
                mainloop.Break
            case ["drop", *objects]:
                print(f'dropping {objects}')
                for obj in objects:
                    character.drop(obj, current_room)
            case ["click", x, y] if 'PC' in character.objects:
                print('emulating click', x, y)
                event.set(Click(position=(x, y)))
            case ["clickd", x, y]:
                event.set(ClickDc((x, y)))
            case ["clickm", *pos, k]:
                event.set(ClickMatchable(pos, k))
            case ["press", key_name] if 'PC' in character.objects:
                print('emulating keypress', key_name)
                event.set(KeyPress(key_name))
            case _:
                print(f"Sorry, I couldn't understand {command!r}")

        match event.get():
            case Click(position=(x, y)):
                print(f'You definitly clicked {x=} {y=}')
            case ClickDc((x, y), kind):
                print(f'clicked (dataclass) {kind=} {x=} {y=}')
            case ClickMatchable((x, y), kind):
                print(f'clicked (__match_args__) {kind=} {x=} {y=}')
            case KeyPress(key_name="Q") | KeyPress(key_name="q"):
                mainloop.Break
            case KeyPress(key_name="up_arrow"):
                current_room = current_room.neighbor('north')
            case KeyPress(key_name="s") if 'Bed' in character.objects:
                print('zzz')
            case KeyPress():
                print('keystroke ignored')
                pass # Ignore other keystrokes
            case False:
                print('no event')
            case other_event:
                raise ValueError(f"Unrecognized event: {other_event}")

if __name__ == '__main__':
    play()
