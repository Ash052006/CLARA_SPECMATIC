from mcp.google_calendar_server import (
    GoogleCalendarServer
)

from mcp.gmail_server import (
    GmailServer
)


class MCPRegistry:

    def __init__(self):

        self.servers = {

            "CalendarTool":
            GoogleCalendarServer(),

            "EmailTool":
            GmailServer()
        }

    def get_server(
        self,
        tool_name
    ):

        return self.servers.get(
            tool_name
        )