class PreferenceMemory:

    def __init__(self):

        self.preferences = {}
        self.history = {}

    def save(self,key,value):

        self.preferences[key]=value

    def get(self,key):

        return self.preferences.get(key)

    def get_all(self):

        return self.preferences

    def add_history(self,key,value):

        if key not in self.history:
            self.history[key]=[]

        self.history[key].append(value)

    def get_history(self,key):

        return self.history.get(key,[])