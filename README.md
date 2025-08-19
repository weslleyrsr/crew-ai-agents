# README — Research & Write Article with an Agentic Crew

## Overview
This project uses a simple “agentic” workflow to research, write, and edit a blog article on a given topic. It defines three collaborating agents:
- Content Planner: researches and outlines the article.
- Content Writer: writes the article based on the plan.
- Editor: reviews and polishes the final draft.

You run the workflow from a Jupyter Notebook and receive a final Markdown article as output.

## What’s Included
- A Jupyter Notebook that:
  - Configures three CrewAI agents (Planner, Writer, Editor)
  - Creates tasks for research/outline, writing, and editing
  - Runs the crew on an input topic
  - Renders the resulting article

## Requirements
- Python 3.13 (recommended; project is set up for Python 3.13.x)
- Jupyter environment (e.g., JupyterLab or VS Code with Python/Jupyter extensions)
- An OpenAI API key

## Installation
1) Create and activate a virtual environment (recommended):
- macOS/Linux:
```shell script
# Bash
python3 -m venv .venv
source .venv/bin/activate
```


- Windows (PowerShell):
```textmate
# PowerShell
python -m venv .venv
.venv\Scripts\Activate.ps1
```


2) Install dependencies:
```shell script
# Bash
pip install --upgrade pip
pip install crewai==0.28.8 crewai_tools==0.1.6 langchain_community==0 jupyter
```


Notes:
- The notebook also uses IPython’s display utilities; installing jupyter pulls these in.
- If you already have Jupyter installed, you can skip adding it again.

## Environment Variables
You must set your OpenAI API key in the environment before running.

- macOS/Linux (bash/zsh):
```shell script
# Bash
export OPENAI_API_KEY='YOUR_OPENAI_API_KEY'
export OPENAI_MODEL_NAME='gpt-3.5-turbo'   # default used in the notebook
```


- Windows (PowerShell):
```textmate
# PowerShell
setx OPENAI_API_KEY "YOUR_OPENAI_API_KEY"
setx OPENAI_MODEL_NAME "gpt-3.5-turbo"
# Restart your terminal/session so the variables are available
```


Tip: The repository’s .gitignore ignores a .env file. You can optionally store variables in a local .env (but don’t commit it) and load them in your shell with your preferred method.

## Running the Notebook
1) Start Jupyter:
```shell script
# Bash
jupyter notebook
# or
jupyter lab
```


2) Open research_write_article.ipynb.

3) Run all cells in order:
- The notebook validates that OPENAI_API_KEY is set.
- It configures the agents and tasks.
- It kicks off the crew on a default topic (“Agentic AI”).
- It displays the resulting article in Markdown.

4) Change the topic:
- In the “Running the crew” cell, modify:
```python
# Python
topic = "Your Desired Topic"
result = crew.kickoff(inputs={"topic": topic})
```

- Re-run that cell (and the final display cell).

## How It Works (Conceptual)
- Planner Agent: Produces an outline, audience analysis, and SEO keywords for {topic}.
- Writer Agent: Drafts the article based on the plan, following the requested structure and style.
- Editor Agent: Reviews for clarity, grammar, and adherence to brand voice.

Each agent receives a role, a goal, and a backstory to guide behavior. Tasks specify what to produce (expected_output) and are assigned to the appropriate agent. The Crew orchestrates execution.

## Troubleshooting
- Missing OPENAI_API_KEY:
  - The notebook will raise an error with instructions. Ensure you exported the variable in the same shell/session you’re using to launch Jupyter.
- Permission/Path issues on Windows:
  - After setx, open a new terminal before starting Jupyter so environment changes are picked up.
- Rate limits or API errors:
  - Try again later, or change the model via OPENAI_MODEL_NAME.
- Dependency conflicts:
  - Use a fresh virtual environment and install the pinned versions listed above.

## Security Notes
- Treat your API key like a password. Do not commit it to version control.
- Prefer environment variables over hardcoding keys inside notebooks or scripts.

## Example Script (Optional, run outside Jupyter)
If you prefer running via a Python script, you can adapt the notebook logic as follows:

```python
# Python
import os
from crewai import Agent, Task, Crew

def create_planner_agent(*, allow_delegation: bool = False, verbose: bool = True) -> Agent:
    return Agent(
        role="Content Planner",
        goal="Plan engaging and factually accurate content on {topic}",
        backstory=("You're working on planning a blog article about the topic: {topic}. "
                   "You collect information that helps the audience learn something "
                   "and make informed decisions. Your work is the basis for "
                   "the Content Writer to write an article on this topic."),
        allow_delegation=allow_delegation,
        verbose=verbose,
    )

def create_writer_agent(*, allow_delegation: bool = False, verbose: bool = True) -> Agent:
    return Agent(
        role="Content Writer",
        goal="Write insightful and factually accurate opinion piece about the topic: {topic}",
        backstory=("You're working on writing a new opinion piece about the topic: {topic}. "
                   "You base your writing on the work of the Content Planner, who provides an outline "
                   "and relevant context about the topic. You follow the main objectives and direction "
                   "of the outline, as provided by the Content Planner. You also provide objective and "
                   "impartial insights and back them up with information provided by the Content Planner. "
                   "You acknowledge when your statements are opinions."),
        allow_delegation=allow_delegation,
        verbose=verbose,
    )

def create_editor_agent(*, allow_delegation: bool = False, verbose: bool = True) -> Agent:
    return Agent(
        role="Editor",
        goal="Edit a given blog post to align with the writing style of the organization.",
        backstory=("You are an editor who receives a blog post from the Content Writer. "
                   "Your goal is to review the blog post to ensure that it follows "
                   "journalistic best practices, provides balanced viewpoints when providing "
                   "opinions or assertions, and avoids major controversial topics or opinions when possible."),
        allow_delegation=allow_delegation,
        verbose=verbose,
    )

def create_plan_task(*, agent: Agent) -> Task:
    return Task(
        description=(
            "1. Prioritize the latest trends, key players, and noteworthy news on {topic}.\n"
            "2. Identify the target audience, considering their interests and pain points.\n"
            "3. Develop a detailed content outline including an introduction, key points, and a call to action.\n"
            "4. Include SEO keywords and relevant data or sources."
        ),
        expected_output=("A comprehensive content plan document with an outline, audience analysis, "
                         "SEO keywords, and resources."),
        agent=agent,
    )

def create_write_task(*, agent: Agent) -> Task:
    return Task(
        description=(
            "1. Use the content plan to craft a compelling blog post on {topic}.\n"
            "2. Incorporate SEO keywords naturally.\n"
            "3. Sections/Subtitles are properly named in an engaging manner.\n"
            "4. Ensure the post is structured with an engaging introduction, insightful body, "
            "and a summarizing conclusion.\n"
            "5. Proofread for grammatical errors and alignment with the brand's voice.\n"
        ),
        expected_output=("A well-written blog post in markdown format, ready for publication, "
                         "each section should have 2 or 3 paragraphs."),
        agent=agent,
    )

def create_edit_task(*, agent: Agent) -> Task:
    return Task(
        description=("Proofread the given blog post for grammatical errors and "
                     "alignment with the brand's voice."),
        expected_output=("A well-written blog post in markdown format, "
                         "ready for publication, each section should have 2 or 3 paragraphs."),
        agent=agent,
    )

def main():
    # Ensure environment variables are set
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("Missing OPENAI_API_KEY. Set it in your environment.")
    os.environ.setdefault("OPENAI_MODEL_NAME", "gpt-3.5-turbo")

    planner = create_planner_agent()
    writer = create_writer_agent()
    editor = create_editor_agent()

    plan = create_plan_task(agent=planner)
    write = create_write_task(agent=writer)
    edit = create_edit_task(agent=editor)

    crew = Crew(
        agents=[planner, writer, editor],
        tasks=[plan, write, edit],
        verbose=True,
    )

    topic = "Agentic AI"  # change as needed
    result = crew.kickoff(inputs={"topic": topic})
    print(getattr(result, "raw", str(result)))

if __name__ == "__main__":
    main()
```