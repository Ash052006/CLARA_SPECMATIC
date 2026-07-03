from mcp.base_server import MCPServer


class CalendarServer(MCPServer):

    def execute(self, action, context):

        if action == "create_meeting":

            entities = context.get(
                "entities",
                {}
            )
            print("ENTITIES:", entities)
            meeting_time = entities.get(
                "datetime"
            )

            if meeting_time:

                return {
                    "status": "success",
                    "message":
                    f"Meeting scheduled for "
                    f"{meeting_time.strftime('%d-%m-%Y %I:%M %p')}"
                }

            return {
                "status": "error",
                "message":
                "Could not determine meeting time"
            }