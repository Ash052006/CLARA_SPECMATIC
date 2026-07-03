SAMPLE_MESSAGES = [
    "What time is my next meeting?",
    "Please read my latest emails.",
    "Schedule a project sync tomorrow at 3 PM.",
    "Can you search email from alex@example.com about Q2?",
]

EDGE_CASE_MESSAGES = [
    "hello",
    "Please summarize my schedule " * 40,
    "Symbols !@#$%^&*() and unicode-friendly text cafe",
]

ERROR_MESSAGES = {
    "blank": "   ",
    "server_error": "raise error",
}
