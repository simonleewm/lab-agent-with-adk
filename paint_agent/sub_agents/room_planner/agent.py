import os
from dotenv import load_dotenv
from google.adk.agents import Agent
from .sub_agents.coverage_calculator.agent import coverage_calculator_agent

load_dotenv()

room_planner_agent = Agent(
    name="room_planner_agent",
    model=os.getenv("MODEL"),
    instruction=f"""
    - Find out how many rooms the user would like to paint and what we should call each room.
    - Have them pick a color for each room. Based on the {{ selected_paint? }}, show the corresponding images
      in an img tag with a height attribute of 300px:
        - Project Paint: https://storage.cloud.google.com/{os.getenv("RESOURCES_BUCKET")}/project_paint.png
        - SureCoverage: https://storage.cloud.google.com/{os.getenv("RESOURCES_BUCKET")}/surecoverage.png
        - EcoGreen: https://storage.cloud.google.com/{os.getenv("RESOURCES_BUCKET")}/ecogreens.png
        - Forever Paint: https://storage.cloud.google.com/{os.getenv("RESOURCES_BUCKET")}/forever_paint.png
    - To calculate the paint needed for each room, transfer to the 'coverage_calculator_agent'
    """,
    sub_agents=[coverage_calculator_agent],
)
