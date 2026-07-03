from datetime import datetime, timedelta
import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

from mcp.base_server import MCPServer


SCOPES = [
    "https://www.googleapis.com/auth/calendar"
]


class GoogleCalendarServer(MCPServer):

    def get_service(self):

        creds = None

        if os.path.exists(
            "token.json"
        ):

            creds = (
                Credentials
                .from_authorized_user_file(
                    "token.json",
                    SCOPES
                )
            )

        if (
            not creds
            or not creds.valid
        ):

            if (
                creds
                and creds.expired
                and creds.refresh_token
            ):

                creds.refresh(
                    Request()
                )

            else:

                flow = (
                    InstalledAppFlow
                    .from_client_secrets_file(
                        "credentials.json",
                        SCOPES
                    )
                )

                creds = (
                    flow.run_local_server(
                        port=0
                    )
                )

            with open(
                "token.json",
                "w"
            ) as token:

                token.write(
                    creds.to_json()
                )

        return build(
            "calendar",
            "v3",
            credentials=creds
        )

    def execute(
    self,
    action,
    context
):

        service = (
            self.get_service()
        )

        entities = context.get(
            "entities",
            {}
        )

        # -------------------------
        # CREATE MEETING
        # -------------------------

        if action == "create_meeting":

            start_time = entities.get(
                "datetime"
            )
            print("MEETING TIME:", start_time)
            if not start_time:

                return {
                    "status": "error",
                    "message": "Could not determine meeting time"
                }

            end_time = (
                start_time
                + timedelta(hours=1)
            )

            event = {

                "summary":
                "CLARA Meeting",

                "start": {

                    "dateTime":
                    start_time.isoformat(),

                    "timeZone":
                    "Asia/Kolkata"
                },

                "end": {

                    "dateTime":
                    end_time.isoformat(),

                    "timeZone":
                    "Asia/Kolkata"
                }
            }

            created_event = (
                service.events()
                .insert(
                    calendarId="primary",
                    body=event
                )
                .execute()
            )

            return {

                "status":
                "success",

                "message":
                "Google Calendar event created",

                "event_id":
                created_event["id"],

                "event_link":
                created_event.get(
                    "htmlLink"
                )
            }

        # -------------------------
        # CREATE HOLIDAY
        # -------------------------

        elif action == "create_holiday":

            holiday_date = (
                datetime.now()
                + timedelta(days=1)
            ).date()

            next_day = (
                holiday_date
                + timedelta(days=1)
            )

            event = {

                "summary":
                "Holiday",

                "start": {

                    "date":
                    str(holiday_date)
                },

                "end": {

                    "date":
                    str(next_day)
                }
            }

            created_event = (
                service.events()
                .insert(
                    calendarId="primary",
                    body=event
                )
                .execute()
            )

            return {

                "status":
                "success",

                "message":
                "Holiday created in Google Calendar",

                "event_id":
                created_event["id"],

                "event_link":
                created_event.get(
                    "htmlLink"
                )
            }

# -------------------------
# LIST EVENTS
# -------------------------

        elif action == "list_events":

            from datetime import timezone

            start = (
                datetime.now(timezone.utc)
                .replace(
                    hour=0,
                    minute=0,
                    second=0,
                    microsecond=0
                )
                + timedelta(days=1)
            )

            end = (
                start
                + timedelta(days=1)
            )

            try:

                events_result = (
                    service.events()
                    .list(
                        calendarId="primary",
                        timeMin=start.isoformat(),
                        timeMax=end.isoformat(),
                        singleEvents=True,
                        orderBy="startTime"
                    )
                    .execute()
                )

                events = (
                    events_result.get(
                        "items",
                        []
                    )
                )

                event_list = []

                for event in events:

                    start_info = event.get(
                        "start",
                        {}
                    )

                    event_list.append({

                        "title":
                        event.get(
                            "summary",
                            "Untitled Event"
                        ),

                        "start":
                        start_info.get(
                            "dateTime",
                            start_info.get(
                                "date",
                                "Unknown"
                            )
                        )
                    })

                return {

                    "status":
                    "success",

                    "count":
                    len(event_list),

                    "events":
                    event_list
                }

            except Exception as e:

                return {

                    "status":
                    "error",

                    "message":
                    str(e)
                }
        # -------------------------
        # DELETE EVENT
        # -------------------------

        elif action == "delete_event":

            from datetime import timezone

            start = (
                datetime.now(timezone.utc)
                .replace(
                    hour=0,
                    minute=0,
                    second=0,
                    microsecond=0
                )
                + timedelta(days=1)
            )

            end = (
                start
                + timedelta(days=1)
            )

            events_result = (
                service.events()
                .list(
                    calendarId="primary",
                    timeMin=start.isoformat(),
                    timeMax=end.isoformat(),
                    singleEvents=True,
                    orderBy="startTime"
                )
                .execute()
            )

            events = (
                events_result.get(
                    "items",
                    []
                )
            )

            if not events:

                return {

                    "status":
                    "error",

                    "message":
                    "No events found"
                }

            event = events[0]

            service.events().delete(
                calendarId="primary",
                eventId=event["id"]
            ).execute()

            return {

                "status":
                "success",

                "message":
                f"Deleted event: {event.get('summary')}",

                "event_id":
                event["id"]
            }
        # -------------------------
        # UPDATE EVENT
        # -------------------------

        elif action == "update_event":

            from datetime import timezone

            start = (
                datetime.now(timezone.utc)
                .replace(
                    hour=0,
                    minute=0,
                    second=0,
                    microsecond=0
                )
                + timedelta(days=1)
            )

            end = start + timedelta(days=1)

            events_result = (
                service.events()
                .list(
                    calendarId="primary",
                    timeMin=start.isoformat(),
                    timeMax=end.isoformat(),
                    singleEvents=True,
                    orderBy="startTime"
                )
                .execute()
            )

            events = (
                events_result.get(
                    "items",
                    []
                )
            )

            if not events:

                return {

                    "status":
                    "error",

                    "message":
                    "No events found"
                }

            event = events[0]

           

            new_start = entities.get(
                "datetime"
            )

            print("UPDATE TIME:", new_start)

            if not new_start:

                return {
                    "status": "error",
                    "message": "Could not determine new meeting time"
                }

            new_end = (
                new_start
                + timedelta(hours=1)
            )

            new_end = (
                new_start
                + timedelta(hours=1)
            )

            event["start"] = {

                "dateTime":
                new_start.isoformat(),

                "timeZone":
                "Asia/Kolkata"
            }

            event["end"] = {

                "dateTime":
                new_end.isoformat(),

                "timeZone":
                "Asia/Kolkata"
            }

            updated_event = (
                service.events()
                .update(
                    calendarId="primary",
                    eventId=event["id"],
                    body=event
                )
                .execute()
            )

            return {

                "status":
                "success",

                "message":
                "Event updated",

                "event_id":
                updated_event["id"],

                "new_time":
                new_start.isoformat()
            }

        # -------------------------
        # UNKNOWN ACTION
        # -------------------------

        return {

            "status":
            "error",

            "message":
            "Unknown action"
        }