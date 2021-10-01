import os
import time
from datetime import datetime
from pathlib import Path
from pprint import pprint

import dotenv
from bs4 import BeautifulSoup
from intercom.client import Client

dotenv.load_dotenv(override=True)

intercom = Client(personal_access_token=os.environ["ACCESS_TOKEN"])


def main():
    for convo in intercom.conversations.find_all():
        export_conversation(convo)
        time.sleep(2)


def export_conversation(convo):
    conversation = intercom.conversations.find(id=convo.id)

    datetime = conversation.created_at.strftime("%Y-%m-%d %H:%M")

    body = f"Created at: {datetime}\n\n" "---\n\n"

    text_parts = []
    for part in conversation.conversation_parts:
        text = part_to_text(part)

        if not text:
            continue

        text_parts.append(text)

    body += "\n\n".join(text_parts)

    filename = f"{conversation.created_at.strftime('%y-%m-%d_%H.%M.%S')}.txt"
    conversations_dir = Path(os.environ["CONVERSATIONS_DIR"])

    if not conversations_dir.exists():
        conversations_dir.mkdir(parents=True)
    filepath = os.path.join(conversations_dir, filename)

    with open(filepath, "w") as fp:
        fp.write(body)


def part_to_text(part):
    time = part.created_at.strftime("%H:%M")
    author = (
        f"{part.author.name} <{part.author.email}>"
        if part.author.name
        else part.author.email
    )
    body = BeautifulSoup(part.body, "html.parser").get_text() if part.body else ""

    return f"{time} | {author}: {body}"


if __name__ == "__main__":
    main()
