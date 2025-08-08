from event import Event

class SomeClass:
    def __init__(self):
        # Private event variable
        self.__event = Event()
        # Public event variable (decorator)
        self.event = self.__event.on

if __name__ == "__main__":
    some = SomeClass()
