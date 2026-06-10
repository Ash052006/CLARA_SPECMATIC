from email.mime.text import MIMEText
import base64
import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

from mcp.base_server import MCPServer


SCOPES = [
    "https://www.googleapis.com/auth/gmail.send",
    "https://www.googleapis.com/auth/gmail.readonly"
]


class GmailServer(MCPServer):

    def get_service(self):

        creds = None

        if os.path.exists(
            "gmail_token.json"
        ):

            creds = (
                Credentials
                .from_authorized_user_file(
                    "gmail_token.json",
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
                "gmail_token.json",
                "w"
            ) as token:

                token.write(
                    creds.to_json()
                )

        return build(
            "gmail",
            "v1",
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

        # -------------------------
        # SEND EMAIL
        # -------------------------

        if action == "send_email":

            try:

                entities = context.get(
                    "entities",
                    {}
                )

                recipient = entities.get(
                    "recipient",
                    "viratplay21@gmail.com"
                )

                subject = entities.get(
                    "subject",
                    "CLARA Email"
                )

                body = entities.get(
                    "body",
                    "This email was sent by CLARA."
                )

                message = MIMEText(
                    body
                )

                message["to"] = recipient

                message["subject"] = (
                    subject
                )

                raw = (
                    base64
                    .urlsafe_b64encode(
                        message.as_bytes()
                    )
                    .decode()
                )

                sent_message = (
                    service.users()
                    .messages()
                    .send(
                        userId="me",
                        body={
                            "raw": raw
                        }
                    )
                    .execute()
                )

                return {

                    "status":
                    "success",

                    "message":
                    "Email sent",

                    "email_id":
                    sent_message["id"],

                    "recipient":
                    recipient,

                    "subject":
                    subject
                }

            except Exception as e:

                return {

                    "status":
                    "error",

                    "message":
                    str(e)
                }
        # -------------------------
        # READ EMAILS
        # -------------------------

        elif action == "read_emails":

            try:

                results = (
                    service.users()
                    .messages()
                    .list(
                        userId="me",
                        maxResults=5
                    )
                    .execute()
                )

                messages = (
                    results.get(
                        "messages",
                        []
                    )
                )

                emails = []

                for msg in messages:

                    full_message = (
                        service.users()
                        .messages()
                        .get(
                            userId="me",
                            id=msg["id"]
                        )
                        .execute()
                    )

                    headers = (
                        full_message["payload"]
                        .get(
                            "headers",
                            []
                        )
                    )

                    subject = "No Subject"

                    sender = "Unknown"

                    for header in headers:

                        if header["name"] == "Subject":

                            subject = (
                                header["value"]
                            )

                        if header["name"] == "From":

                            sender = (
                                header["value"]
                            )

                    emails.append({

                        "from":
                        sender,

                        "subject":
                        subject
                    })

                return {

                    "status":
                    "success",

                    "count":
                    len(emails),

                    "emails":
                    emails
                }

            except Exception as e:

                return {

                    "status":
                    "error",

                    "message":
                    str(e)
        }
        # -------------------------
        # SEARCH EMAILS
        # -------------------------

        elif action == "search_emails":

            try:

                entities = context.get(
                    "entities",
                    {}
                )

                query = entities.get(
                    "search_query",
                    ""
                )

                results = (
                    service.users()
                    .messages()
                    .list(
                        userId="me",
                        q=query,
                        maxResults=10
                    )
                    .execute()
                )

                messages = (
                    results.get(
                        "messages",
                        []
                    )
                )

                emails = []

                for msg in messages:

                    full_message = (
                        service.users()
                        .messages()
                        .get(
                            userId="me",
                            id=msg["id"]
                        )
                        .execute()
                    )

                    subject = "No Subject"
                    sender = "Unknown"

                    for header in (
                        full_message["payload"]
                        .get(
                            "headers",
                            []
                        )
                    ):

                        if header["name"] == "Subject":

                            subject = (
                                header["value"]
                            )

                        elif header["name"] == "From":

                            sender = (
                                header["value"]
                            )

                    emails.append({

                        "from":
                        sender,

                        "subject":
                        subject,

                        "snippet":
                        full_message.get(
                            "snippet",
                            ""
                        )
                    })

                return {

                    "status":
                    "success",

                    "query":
                    query,

                    "count":
                    len(emails),

                    "emails":
                    emails
                }

            except Exception as e:

                return {

                    "status":
                    "error",

                    "message":
                    str(e)
                }
        # -------------------------
        # REPLY TO LATEST EMAIL
        # -------------------------

        elif action == "reply_latest_email":

            try:

                entities = context.get(
                    "entities",
                    {}
                )

                reply_body = entities.get(
                    "reply_body",
                    "Thank you."
                )

                results = (
                    service.users()
                    .messages()
                    .list(
                        userId="me",
                        maxResults=1
                    )
                    .execute()
                )

                messages = (
                    results.get(
                        "messages",
                        []
                    )
                )

                if not messages:

                    return {
                        "status": "error",
                        "message": "No emails found"
                    }

                latest_id = messages[0]["id"]

                latest_email = (
                    service.users()
                    .messages()
                    .get(
                        userId="me",
                        id=latest_id
                    )
                    .execute()
                )

                sender = None
                subject = "No Subject"

                headers = (
                    latest_email["payload"]
                    .get(
                        "headers",
                        []
                    )
                )

                for header in headers:

                    if header["name"] == "From":

                        sender = (
                            header["value"]
                        )

                    elif header["name"] == "Subject":

                        subject = (
                            header["value"]
                        )

                if not sender:

                    return {
                        "status": "error",
                        "message": "Sender not found"
                    }

                message = MIMEText(
                    reply_body
                )

                message["to"] = sender
                message["subject"] = (
                    f"Re: {subject}"
                )

                raw = (
                    base64
                    .urlsafe_b64encode(
                        message.as_bytes()
                    )
                    .decode()
                )

                sent_message = (
                    service.users()
                    .messages()
                    .send(
                        userId="me",
                        body={
                            "raw": raw
                        }
                    )
                    .execute()
                )

                return {

                    "status":
                    "success",

                    "message":
                    "Reply sent",

                    "recipient":
                    sender,

                    "subject":
                    f"Re: {subject}",

                    "email_id":
                    sent_message["id"]
                }

            except Exception as e:

                return {

                    "status":
                    "error",

                    "message":
                    str(e)
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