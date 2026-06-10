import json


class LongTermMemory:

    def __init__(self):

        self.file = "storage/memory.json"

    def save(self,data):

        with open(
            self.file,
            "w"
        ) as f:

            json.dump(
                data,
                f,
                indent=4
            )

    def load(self):

        try:

            with open(
                self.file,
                "r"
            ) as f:

                return json.load(f)

        except:

            return {}