from dotenv import load_dotenv
from google.adk.agents import Agent
import os

from google.adk.tools import VertexAiSearchTool, ToolContext

load_dotenv()

SEARCH_ENGINE_PATH = f"projects/{os.getenv('GOOGLE_CLOUD_PROJECT')}/locations/global/collections/default_collection/engines/{os.getenv('SEARCH_ENGINE_ID')}"
paint_search_tool = VertexAiSearchTool(search_engine_id=SEARCH_ENGINE_PATH)

search_agent = Agent(
    name="search_agent",
    model=os.getenv("MODEL"),
    instruction="""
    If the user asked for specific paints, look up information on requested paints.
    Otherwise, provide the user information about all Cymbal Shops paints, including price
    and coverage rate.
    """,
    tools=[paint_search_tool],
)
