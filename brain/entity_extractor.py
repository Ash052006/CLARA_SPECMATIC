import dateparser.search
import re

class EntityExtractor:


    def extract(self, message):

        entities = {}

        cleaned_message = message

        # --------------------
        # Extract Email
        # --------------------

        email_match = re.search(
            r'[\w\.-]+@[\w\.-]+\.\w+',
            message
        )

        if email_match:

            entities["recipient"] = (
                email_match.group()
            )

        # --------------------
        # Extract Subject
        # --------------------

        if "subject" in message.lower():

            subject_text = (
                message.lower()
                .split("subject", 1)[1]
            )

            if "saying" in subject_text:

                subject_text = (
                    subject_text
                    .split("saying", 1)[0]
                )

            entities["subject"] = (
                subject_text.strip()
            )

        # --------------------
        # Extract Email Body
        # --------------------

        if "saying" in message.lower():

            body = (
                message
                .split(
                    "saying",
                    1
                )[1]
                .strip()
            )

            entities["body"] = body

        # --------------------
        # Smart DateTime Extraction
        # --------------------

        dates = dateparser.search.search_dates(
            cleaned_message,
            settings={
                "PREFER_DATES_FROM": "future"
            }
        )

        if dates:

            parsed_datetime = dates[0][1]

            entities["datetime"] = (
                parsed_datetime
            )

            entities["date"] = (
                parsed_datetime.strftime(
                    "%Y-%m-%d"
                )
            )

            entities["time"] = (
                parsed_datetime.strftime(
                    "%H:%M"
                )
            )

        # --------------------
        # Email Search Query
        # --------------------

        if "from" in message.lower():

            sender_query = (
                message.lower()
                .split("from", 1)[1]
                .strip()
            )

            entities["search_query"] = (
                sender_query
            )

        # --------------------
        # Reply Body
        # --------------------

        if "reply" in message.lower():

            if "saying" in message.lower():

                entities["reply_body"] = (
                    message
                    .split("saying", 1)[1]
                    .strip()
                )

        return entities

