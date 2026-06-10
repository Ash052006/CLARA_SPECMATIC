from mcp.registry import MCPRegistry


class ToolExecutor:

    def __init__(self):

        self.registry = MCPRegistry()

    def execute(self, plan, context):

        results = []

        for step in plan:

            tool = step["tool"]

            action = step["action"]

            server = self.registry.get_server(
                tool
            )

            if server:

                result = server.execute(
                    action,
                    context
                )

                results.append(result)

        return results