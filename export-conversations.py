import os
import time
from pathlib import Path

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
    delivered_as = conversation.source.delivered_as
    print(f"Exporting '{delivered_as}' conversation from: {datetime}")

    text = f"Created at: {datetime}\n\n" "---\n\n"

    author = get_author(conversation.source)
    body = html_to_text(conversation.source.body)
    text_parts = [create_chat_line(conversation.created_at, author, body)]

    for part in conversation.conversation_parts:
        line = part_to_text(part)

        if not line:
            continue

        text_parts.append(line)

    text += "\n\n".join(text_parts)

    filename = f"{conversation.created_at.strftime('%y-%m-%d_%H.%M.%S')}.txt"
    conversations_dir = Path(os.environ["CONVERSATIONS_DIR"])
    conversations_dir = Path(os.path.join(conversations_dir, str(delivered_as)))

    if not conversations_dir.exists():
        conversations_dir.mkdir(parents=True)
    filepath = os.path.join(conversations_dir, filename)

    with open(filepath, "w") as fp:
        fp.write(text)


def part_to_text(part):
    if not part.body:
        return None

    time = part.created_at
    author = get_author(part)
    body = html_to_text(part.body)

    return create_chat_line(time, author, body)


def create_chat_line(time, author, body):
    return f"{time.strftime('%H:%M')} | {author}: {body}"


def get_author(part):
    return (
        f"{part.author.name} <{part.author.email}>"
        if part.author.name
        else part.author.email
    )


def html_to_text(html):
    return BeautifulSoup(html, "html.parser").get_text()


if __name__ == "__main__":
    main()
