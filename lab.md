# Deploy an Agent with Agent Development Kit (ADK): Challenge Lab

## Overview

In this lab, you will demonstrate your ability to author agents using the Agent Development Kit (ADK), deploy those agents to Agent Engine, and use them from a web app.

## Objective

In this lab you will:

-   Build an agent with Agent Development Kit (ADK) made up of a root agent and sub-agents.
-   Enable agents with a Vertex AI Search tool and custom function tools.
-   Store agent output in session state and retrieve values from session state for subsequent agent instructions.
-   Deploy your agent to Agent Engine.
-   Query the agent deployed to Agent Engine.

## Challenge Scenario

Cymbal Shops is an American retail chain headquartered in Minneapolis that sells housewares, electronics, and clothing.

Cymbal Shops has expanded into Europe and launched a new Paint Department. It plans to use its new online presence to streamline the way people shop for paint for DIY home renovation projects.

A coworker of yours began to develop an agent, **Paint Agent**, to help the user:

-   select a paint product based on Cymbal Sheets' paint product datasheets
-   choose a color from the selected product line
-   determine how much paint is needed by rooms' dimensions
-   calculate the price based on the selected options

Your coworker, however, got stuck on a bug and left the organization.

You are a new ML Engineer with Cymbal Shops. You've been tasked with completing the deployment of Paint Agent.

---

## Task 1. Install ADK and set up your environment

In this lab environment, the Vertex AI API has been enabled for you. If you were to follow these steps in your own project, you would enable it by navigating to Vertex AI and following the prompt to enable it.

### Prepare a Cloud Shell Editor tab

1.  With your Google Cloud console window selected, open Cloud Shell by pressing the `G` key and then the `S` key on your keyboard. Alternatively, you can click the **Activate Cloud Shell** button in the upper right of the Cloud console.
2.  Click **Continue**.
3.  When prompted to authorize Cloud Shell, click **Authorize**.
4.  In the upper right corner of the Cloud Shell Terminal panel, click the **Open in new window** button.
5.  In the Cloud Shell Terminal, enter the following to open the Cloud Shell Editor to your home directory:

    ```bash
    cloudshell workspace ~
    ```

6.  Close any additional tutorial or Gemini panels that appear on the right side of the screen to save more of your window for your code editor.

Throughout the rest of this lab, you can work in this window as your IDE with the Cloud Shell Editor and Cloud Shell Terminal.

### Download and install ADK and code samples for this lab

1.  Paste the following command into the Cloud Shell Terminal to copy files from a Cloud Storage bucket, creating a project directory with code for this lab:

    ```bash
    gcloud storage cp -r gs://<YOUR_PROJECT_ID>-bucket/adk_challenge_lab .
    ```

2.  Update your `PATH` environment variable and install ADK and other lab requirements by running the following commands in the Cloud Shell Terminal.

    ```bash
    export PATH=$PATH:"/home/${USER}/.local/bin"
    python3 -m pip install "google-adk==1.16.0" -r adk_challenge_lab/requirements.txt
    ```

---

## Task 2. Create an AI Applications search app for paint product info

The paint datasheet has not yet been uploaded for your agent to search.

Deploy an AI Applications data store. This data store will import a datasheet describing Cymbal Shops' paint (which you can preview in a tab in your Incognito window at `https://storage.cloud.google.com/<YOUR_PROJECT_ID>-bucket/Cymbal_Shops_Paint_Datasheets.pdf`). This datasheet will serve as the grounding data source for user queries about your paints.

### Create an AI Applications data store with the following configuration:

| Field                            | Value                                                       |
| -------------------------------- | ----------------------------------------------------------- |
| **Data source**                  | Cloud Storage                                               |
| **Data type**                    | Unstructured documents                                      |
| **Folder or File**               | File                                                        |
| **File to import**               | `<YOUR_PROJECT_ID>-bucket/Cymbal_Shops_Paint_Datasheets.pdf` |
| **Location**                     | global                                                      |
| **Data store name**              | Cymbal Paint                                                |
| **Document parser**              | Layout Parser                                               |
| **Enable table annotation**      | Enabled                                                     |
| **Include ancestor headings in chunks** | Enabled                                                     |

### Create an AI Applications search app with the following configuration:

| Field          | Value              |
| -------------- | ------------------ |
| **App type**   | Custom search (general) |
| **App name**   | Paint Search       |
| **Company name** | Cymbal Shops       |
| **Location**   | global             |
| **Data store** | Cymbal Paint       |

### Configure environment variables

1.  Copy the following commands to a text file and update the `YOUR_ID` value provided to the key `SEARCH_ENGINE_ID` to the ID of the search engine you just created (in the form `paint-search_1756...`):

    ```bash
    cd ~/adk_challenge_lab
    cat << EOF > .env
    GOOGLE_GENAI_USE_VERTEXAI=TRUE
    GOOGLE_CLOUD_PROJECT=<YOUR_PROJECT_ID>
    GOOGLE_CLOUD_LOCATION=us-central1
    RESOURCES_BUCKET=<YOUR_PROJECT_ID>-bucket
    MODEL=gemini-1.5-flash-001
    SEARCH_ENGINE_ID=YOUR_ID
    EOF
    ```

2.  Run your edited commands in the Cloud Shell Terminal to create a `.env` file with model authentication and configuration variables.
    > **Note**: To view a hidden file (indicated by a file beginning with a period), you can use the Cloud Shell Editor menus to enable **View > Toggle Hidden Files**.

3.  Copy the `.env` file to the agent directory to provide your agent necessary authentication configurations once it is deployed:

    ```bash
    cp .env paint_agent/.env
    ```

---

## Task 3. Debug the Paint Agent

A coworker of yours had begun work on the Paint Agent, but got stuck. You'll need to pick up where they left off -- including fixing a bug they left behind -- to complete and deploy the agent.

1.  In the Cloud Shell Terminal, run the current version of the agent with:

    ```bash
    adk run paint_agent
    ```

2.  When the `[user]:` prompt appears, enter:

    ```
    hello
    ```

3.  If the agent follows up asking if you'd like to learn more about Cymbal Shops' paints, reply:

    ```
    yes
    ```

**Expected output for the above commands ends with:**

```
google.genai.errors.ClientError: 400 INVALID_ARGUMENT. {'error': {'code': 400, 'message': 'Multiple tools are supported only when they are all search tools.', 'status': 'INVALID_ARGUMENT'}}
```

In the following steps, you will resolve this error.

Open the file `adk_challenge_lab/paint_agent/agent.py` and inspect the lists of sub-agents and tools that the `root_agent` utilizes. Notice that it includes sub-agents. Even if there were no other tools, if the agent includes sub-agents and a search tool, this error would still be seen as transferring to sub-agents invokes an implicit `transfer_to_agent` tool.

The `root_agent`'s tool is not a search tool, so at least one of the sub-agents must invoke a search tool. Explore the sub-agents found in the `sub_agents` directory to find the search tool being used (in this case a `VertexAiSearchTool`).

While a search tool cannot be combined with other non-search tools in an agent (even by using it in a sub-agent as seen here), ADK does provide a tool named `AgentTool` that can wrap an isolated agent that uses a search tool. Then that agent-as-tool can be used with other tools.

Back in the `root_agent`'s file `adk_challenge_lab/paint_agent/agent.py`, add an `AgentTool()` to the `root_agent`'s list of tools. Provide the `AgentTool()` the following arguments:

-   `agent` should be set to the sub-agent that uses the search tool you uncovered above.
-   `skip_summarization` should be set to `False` because you would like the agent to report on what the search tool has returned.
-   Remove that sub-agent from the `sub_agents` list.

Save the file.

> **Note**: Continue only after your data store has been created and your document indexed. You can monitor this status in the **AI Applications > Data Stores > Cymbal Paint** data store on the **Documents** tab.

In the Cloud Shell Terminal, run the agent again with:

```bash
adk run paint_agent
```

You should now be able to chat with the agent and get information on Cymbal Shops paint.

Get the agent to tell you the price of the `EcoGreens` and `Forever Paint` paints.

When you are finished chatting with the agent via the command-line interface, type `exit` to end the conversation.

---

## Task 4. Save and utilize shared state

Your `root_agent` imports and uses a `set_session_value` tool from `adk_challenge_lab/paint_agent/tools.py`, but it is not fully implemented.

1.  Update the `set_session_value` function in the file `adk_challenge_lab/paint_agent/tools.py` to store key-value pairs in the `ToolContext`'s state dictionary.
2.  Update the function's response to return a status message of `f"stored '{value}' in '{key}'"`.
3.  Open the `agent.py` file associated with the `coverage_calculator_agent` (sub-agent of the `room_planner`, which is a sub-agent of your `root_agent`).
4.  Notice that its instructions are not correctly loading values from the state dictionary. Update the instruction to replace terms in `ALL CAPS` to instead use ADK's key templating to load state values into instructions.

Test your agent with:

```bash
adk web
```

Select `paint_agent`.

You should now be able to have the following conversation with your agent:

| You                                           | Agent Response                                                                                             |
| --------------------------------------------- | ---------------------------------------------------------------------------------------------------------- |
| hello                                         | [Offers to share information about Cymbal Shops' paints]                                                   |
| yes                                           | [Shares information about paint products, i.e. Project Paint, EcoGreens, SureCoverage, Forever Paint.]     |
| I'd like to use EcoGreens                     | [The State tab should show updated state values. Asks how many rooms and what to call each room.]            |
| Just one room, my office                      | [Asks you to select a color for your office.]                                                              |
| Deep Ocean                                    | [Asks you for the room dimensions.]                                                                        |
| 3m by 4m. 3m high. 1 door, 2 windows.         | [Confirms how many coats.]                                                                                 |
| Two coats.                                    | [Calculates you will need X amount of paint and the price.]                                                |

When you are finished chatting with your agent, you can close the Dev UI browser tab.

Select the Cloud Shell Terminal panel and press `CTRL+C` to shut down the server.

---

## Task 5. Deploy to Agent Engine

1.  In Cloud Shell Terminal, make sure you are in the `adk_challenge_lab` directory:

    ```bash
    cd ~/adk_challenge_lab
    ```

2.  Deploy your agent with the appropriate deployment command to deploy the `paint_agent` to Agent Engine, using the following arguments:

    | Parameter        | Argument                               |
    | ---------------- | -------------------------------------- |
    | `--display_name` | "Paint Agent"                          |
    | `--staging_bucket` | `gs://<YOUR_PROJECT_ID>-bucket` |

    As the agent deploys, grant the `Vertex AI User` and `Discovery Engine User` IAM roles to the `Vertex AI Reasoning Engine Service Agent`.

    > **Note**: when deployment is complete, the deployed agent's resource name is printed to the console.

---

## Task 6. Query the deployed agent

1.  In the file `adk_challenge_lab/chainlit_ui/app.py`, find and update the following line with your deployed agent's resource name to load your remote agent:

    ```python
    agent = agent_engines.get('YOUR_AGENT_RESOURCE_NAME')
    ```

2.  Run the UI with the following:

    ```bash
    cd ~/adk_challenge_lab/chainlit_ui
    chainlit run app.py
    ```

**Expected output:**

```
2025-08-25 12:30:00 - Your app is available at http://localhost:8000
```

Click the link for `http://localhost:8000` to open it in a new browser tab.

Have the following conversation with your deployed agent:

| You                                                                                      | Agent Response                                                                                             |
| ---------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------- |
| hello                                                                                    | [Offers to share information about Cymbal Paints]                                                          |
| yes                                                                                      | [Shares information about paint products, i.e. Project Paint, EcoGreens, SureCoverage, Forever Paint ]     |
| I'd like to use Forever Paint                                                            | [Asks how many rooms and what to call each room]                                                           |
| Two rooms. The living room and a baby's room.                                            | [Asks you to select a color for your office.]                                                              |
| "Sunlight through a canvas tent" for the baby's room and "Coffee Cream" for the living room. | [Asks you for the room dimensions]                                                                         |
| The living room is 5m by 4m. 2.5m high. 1 door, 3 windows.                                 | [Requests dimensions for baby's room.]                                                                     |
| The baby's room is 3m by 3m. 2.5m high. 1 door, 1 window.                                  | [Provides one coat estimate and confirms number of coats.]                                                 |
| Always two coats.                                                                        | [Calculates you will need X amount of paint and the price.]                                                |

If you'd like to start a new conversation with your agent, you can click the icon in the upper left to **Create a New Chat**.

---

## Congratulations!

In this lab, you have:

-   Built an agent with Agent Development Kit (ADK) made up of a root agent and sub-agents
-   Enabled agents with a Vertex AI Search tool and custom function tools
-   Stored agent output in a session state dictionary and retrieved values from the session state dictionary for subsequent agent instructions
-   Deployed your agent to Agent Engine
-   Queried the agent deployed to Agent Engine
