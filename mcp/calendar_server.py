from mcp.base_server import MCPServer


class CalendarServer(MCPServer):

    def execute(self, action, context):

        if action == "create_meeting":

            entities = context.get(
                "entities",
                {}
            )

            return {
                "status": "success",
                "message":
                f"Meeting scheduled for "
                f"{entities.get('date','unknown')} "
                f"at {entities.get('time','unknown')}"
            }