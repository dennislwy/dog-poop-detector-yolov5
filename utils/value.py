class ValueTracker:
    def __init__(self, initial_value):
        self.current = initial_value
        self.previous = initial_value

    def update(self, new_value):
        self.previous = self.current
        self.current = new_value

    def changed(self):
        return self.current != self.previous
