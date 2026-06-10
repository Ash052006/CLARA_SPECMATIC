import dateparser.search
import re


class EntityExtractor:

    def extract(self, message):

        entities = {}

        cleaned_message = message

        # --------------------
        # Extract Time
        # --------------------

        time_match = re.search(
            r'\b\d{1,2}(:\d{2})?\s?(AM|PM|am|pm)\b',
            message
        )

        if time_match:

            entities["time"] = (
                time_match.group()
            )

            cleaned_message = (
                cleaned_message.replace(
                    time_match.group(),
                    ""
                )
            )

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
        # Common Date Keywords
        # --------------------

        text = cleaned_message.lower()

        if "tomorrow" in text:

            entities["date"] = (
                "tomorrow"
            )

        elif "today" in text:

            entities["date"] = (
                "today"
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

        else:

            # --------------------
            # DateParser Fallback
            # --------------------

            dates = (
                dateparser.search.search_dates(
                    cleaned_message
                )
            )

            if dates:

                date_text = (
                    dates[0][0]
                    .strip()
                )

                if len(date_text) > 2:

                    entities["date"] = (
                        date_text
                    )

        return entities