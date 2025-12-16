import chainlit as cl
import vertexai
from vertexai import agent_engines
from uuid import uuid4
from dotenv import load_dotenv
import os
from bs4 import BeautifulSoup


load_dotenv()
project_id = os.environ["GOOGLE_CLOUD_PROJECT"]
location = os.environ["GOOGLE_CLOUD_LOCATION"]
bucket_name = f"gs://{project_id}-bucket"

vertexai.init(
    project=project_id,
    location=location,
    staging_bucket=bucket_name,
)

agent = agent_engines.get("projects/141900037650/locations/us-central1/reasoningEngines/6351460859243397120")


def convert_img_tags_to_chainlit_images(msg):
    img_list = []
    soup = BeautifulSoup(msg.content, "html.parser")
    for img_tag in soup.find_all("img"):
        if img_tag.has_attr("src"):
            img = cl.Image(url=img_tag["src"], name="swatch", display="inline")
            img_list.append(img)
    msg.elements = img_list
    msg.content = soup.get_text()
    return msg


@cl.set_starters
async def set_starters():
    return [
        cl.Starter(
            label="Painting Project Help",
            message="Tell me about Cymbal Shops' interior paints.",
            icon="/public/swatches.svg",
        )
    ]


@cl.on_chat_start
def on_chat_start():
    print("A new chat session has started!")
    user_id = "user"
    session_details = agent.create_session(user_id=user_id)
    cl.user_session.set("user_id", user_id)
    cl.user_session.set("session_id", session_details["id"])
    cl.user_session.set(
        "message_history",
        [{"role": "system", "content": "You are a helpful assistant."}],
    )


@cl.on_message
async def main(message: cl.Message):
    message_history = cl.user_session.get("message_history")
    message_history.append({"role": "user", "content": message.content})
    events = agent.stream_query(
        user_id=cl.user_session.get("user_id"),
        session_id=cl.user_session.get("session_id"),
        message=message.content,
    )

    msg = cl.Message(content="")

    # Send a response back to the user
    for event in events:
        print(event)
        for part in event["content"]["parts"]:
            print(part)
            if "text" in part:
                await msg.stream_token(part["text"])
    msg = convert_img_tags_to_chainlit_images(msg)
    message_history.append({"role": "assistant", "content": msg.content})
    await msg.update()
