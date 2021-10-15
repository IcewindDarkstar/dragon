
CHARS_TO_ESCAPE = {'~', '_', '*', '`'}
ESCAPE_CHARACTER = '\\'


def escape_message(message: str) -> str:
    escaped_message = ""
    for char in message:
        if char in CHARS_TO_ESCAPE:
            escaped_message += ESCAPE_CHARACTER
        escaped_message += char
    return escaped_message
