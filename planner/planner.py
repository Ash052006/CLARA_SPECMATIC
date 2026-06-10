class Planner:

    def create_plan(self, context):

        intent = context.get(
            "intent",
            "unknown"
        )

        plan = []

        if intent == "meeting":

            plan = [
                {
                    "tool": "CalendarTool",
                    "action": "create_meeting"
                }
            ]

        elif intent == "holiday":

            plan = [
                {
                    "tool": "CalendarTool",
                    "action": "create_holiday"
                }
            ]

        elif intent == "calendar_query":

            plan = [
                {
                    "tool": "CalendarTool",
                    "action": "list_events"
                }
            ]

        elif intent == "calendar_delete":

            plan = [
                {
                    "tool": "CalendarTool",
                    "action": "delete_event"
                }
            ]
        elif intent == "calendar_update":

            plan = [
                {
                    "tool": "CalendarTool",
                    "action": "update_event"
                }
            ]
        elif intent == "email":

            plan = [
                {
                    "tool": "EmailTool",
                    "action": "send_email"
                }
            ]
        elif intent == "email_query":

            plan = [
                {
                    "tool": "EmailTool",
                    "action": "read_emails"
                }
            ]
        elif intent == "email_search":

            plan = [
                {
                    "tool": "EmailTool",
                    "action": "search_emails"
                }
            ]
        elif intent == "email_reply":

            plan = [
                {
                    "tool": "EmailTool",
                    "action": "reply_latest_email"
                }
            ]
        return plan