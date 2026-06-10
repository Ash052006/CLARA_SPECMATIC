class ToolRouter:

    def route(self, plan):

        tools = []

        for step in plan:

            tools.append(
                step["tool"]
            )

        return tools