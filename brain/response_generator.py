class ResponseGenerator:

    def generate(
        self,
        context,
        preferences
    ):

        intent = context.get(
            "intent",
            "unknown"
        )

        entities = context.get(
            "entities",
            {}
        )

        response = ""

        if intent=="meeting":

            response = (
                "I understood that you want "
                "to schedule a meeting"
            )

            if "date" in entities:

                response += (
                    f" {entities['date']}"
                )

            if "time" in entities:

                response += (
                    f" at {entities['time']}"
                )

            response += "."

        else:

            response = (
                "I understood your request."
            )

        if preferences:

            pref = preferences.get(
                "preferred_meeting_time"
            )

            if pref:

                response += (
                    f" I remember you "
                    f"usually prefer "
                    f"{pref} meetings."
                )

        return response