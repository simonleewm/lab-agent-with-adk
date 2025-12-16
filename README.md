# Paint Agent with Agent Development Kit (ADK)

## Overview

This project demonstrates how to build and deploy a conversational agent using the Agent Development Kit (ADK). The agent, "Paint Agent," assists users in selecting paint products from Cymbal Shops, calculating the required amount of paint for their rooms, and estimating the cost.

The agent is composed of a root agent and several sub-agents, each with specific responsibilities:
- **Root Agent**: The main entry point that interacts with the user, provides information about paint products, and delegates tasks to sub-agents.
- **Search Agent**: A sub-agent responsible for searching Cymbal Shops' paint product datasheets using Vertex AI Search.
- **Room Planner Agent**: A sub-agent that helps users calculate the amount of paint needed based on room dimensions.
- **Coverage Calculator Agent**: A sub-agent of the Room Planner that performs the actual paint coverage calculation.

This project uses a Chainlit UI to provide a user-friendly chat interface for interacting with the deployed agent.

## Prerequisites

- A Google Cloud Project with the Vertex AI API enabled.
- A Cloud Shell environment or a local environment with the Google Cloud SDK installed and configured.
- Python 3.10 or higher.
- A GitHub account.

## Setup

1.  **Clone the repository:**


    ```bash
    git clone https://github.com/simonleewm/lab-agent-with-adk.git
    cd lab-agent-with-adk
    ```

2.  **Set up your environment and install dependencies:**

    Update your `PATH` environment variable and install the required Python packages.

    ```bash
    export PATH=$PATH:"/home/${USER}/.local/bin"
    python3 -m pip install -r requirements.txt
    ```

3.  **Create a Vertex AI Search data store:**

    The agent uses Vertex AI Search to find information about paint products. You need to create a data store and a search app.

    -   In the Google Cloud Console, navigate to **Vertex AI Search and Conversation**.
    -   Create a new **Search** app.
    -   **Data Store Creation:**
        -   Data source: **Cloud Storage**
        -   Data type: **Unstructured documents**
        -   Select the `Cymbal_Shops_Paint_Datasheets.pdf` file from the bucket provided in the lab.
        -   Location: **global**
        -   Data store name: `Cymbal Paint`
        -   Document parser: **Layout Parser**
        -   Enable table annotation: **Enabled**
        -   Include ancestor headings in chunks: **Enabled**
    -   **Search App Configuration:**
        -   App type: **Custom search (general)**
        -   App name: `Paint Search`
        -   Company name: `Cymbal Shops`
        -   Location: **global**
        -   Data store: `Cymbal Paint`

4.  **Create the `.env` file:**

    Create a `.env` file in the root of the project with the following content. Replace `<YOUR_PROJECT_ID>` with your Google Cloud project ID and `<YOUR_SEARCH_ENGINE_ID>` with the ID of the search engine you created in the previous step.

    ```
    GOOGLE_GENAI_USE_VERTEXAI=TRUE
    GOOGLE_CLOUD_PROJECT=<YOUR_PROJECT_ID>
    GOOGLE_CLOUD_LOCATION=us-central1
    MODEL=gemini-1.5-flash-001
    SEARCH_ENGINE_ID=<YOUR_SEARCH_ENGINE_ID>
    ```

5.  **Copy the `.env` file to the `paint_agent` directory:**

    ```bash
    cp .env paint_agent/.env
    ```

## Running the Application

You can run the agent locally using the ADK CLI for testing and debugging.

1.  **Run the agent in the command line:**

    ```bash
    adk run paint_agent
    ```

    You can interact with the agent directly in your terminal.

2.  **Run the agent with the ADK Web UI:**

    ```bash
    adk web
    ```

    This will start a web server with a development UI where you can test your agent.

## Sample Conversation

Here is a sample conversation with the Paint Agent:

**You**: hello
**Agent**: [Offers to share information about Cymbal Shops' paints]
**You**: yes
**Agent**: [Shares information about paint products, i.e. Project Paint, EcoGreens, SureCoverage, Forever Paint.]
**You**: I'd like to use EcoGreens
**Agent**: [The State tab should show updated state values. Asks how many rooms and what to call each room.]
**You**: Just one room, my office
**Agent**: [Asks you to select a color for your office.]
**You**: Deep Ocean
**Agent**: [Asks you for the room dimensions.]
**You**: 3m by 4m. 3m high. 1 door, 2 windows.
**Agent**: [Confirms how many coats.]
**You**: Two coats.
**Agent**: [Calculates you will need X amount of paint and the price.]

## Deployment

To make the agent available for use in other applications, you need to deploy it to Agent Engine.

1.  **Deploy the agent:**

    Run the following command to deploy the `paint_agent` to Agent Engine. Replace `<YOUR_STAGING_BUCKET>` with the name of a Cloud Storage bucket in your project.

    ```bash
    adk deploy agent_engine paint_agent --display_name "Paint Agent" --staging_bucket <YOUR_STAGING_BUCKET>
    ```

    During the deployment process, you will be prompted to grant the `Vertex AI User` and `Discovery Engine User` IAM roles to the Vertex AI Reasoning Engine Service Agent.

2.  **Update the Chainlit UI with the deployed agent's resource name:**

    After the deployment is complete, the agent's resource name will be printed to the console. Copy this resource name.

    Open the `chainlit_ui/app.py` file and replace `YOUR_AGENT_RESOURCE_NAME` with the copied resource name:

    ```python
    agent = agent_engines.get('YOUR_AGENT_RESOURCE_NAME')
    ```

3.  **Run the Chainlit UI:**

    ```bash
    cd chainlit_ui
    chainlit run app.py
    ```

    This will start the Chainlit UI, which is now connected to your deployed agent. You can access the UI at `http://localhost:8000`.

## Learnings

This lab demonstrates the power and flexibility of the Agent Development Kit (ADK) for building complex, multi-turn conversational agents. Key learnings include:

-   **Modular Agent Design**: How to structure an agent with a root agent and multiple sub-agents, each with a specific purpose.
-   **Tool Integration**: How to enable agents with tools, including Vertex AI Search for information retrieval and custom function tools for specific tasks.
-   **State Management**: How to use the `ToolContext` to store and retrieve session state, allowing the agent to remember information across multiple turns of a conversation.
-   **Deployment**: How to deploy an agent to Agent Engine to make it accessible as a scalable, managed service.
-   **Frontend Integration**: How to connect a web application (in this case, a Chainlit UI) to a deployed agent.

## Expected Output

When you run the Chainlit UI, you should see the following in your terminal:

```
2025-08-25 12:30:00 - Your app is available at http://localhost:8000
```

Opening the URL in your browser will show the chat interface where you can interact with the Paint Agent. The agent will be able to answer questions about paint products, help you with calculations, and guide you through the paint selection process.
