class ContextManager:

    def merge(self, old_context, new_context):

        if not old_context:
            return new_context

        merged = old_context.copy()

        # Keep previous intent if confidence is weak
        if (
            new_context["intent"] == "reminder"
            and old_context.get("intent")
        ):
            merged["intent"] = old_context["intent"]

        else:
            merged["intent"] = new_context["intent"]

        # Merge entities properly
        old_entities = old_context.get(
            "entities",
            {}
        )

        new_entities = new_context.get(
            "entities",
            {}
        )

        merged["entities"] = {
            **old_entities,
            **new_entities
        }

        return merged