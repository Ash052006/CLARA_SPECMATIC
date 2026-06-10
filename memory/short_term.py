class ShortTermMemory:

    def __init__(self):
        self.context = {}

    def save(self, key, value):

        self.context[key] = value

    def get(self, key):

        return self.context.get(key)

    def get_all(self):

        return self.context

    def clear(self):

        self.context = {}
