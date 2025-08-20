# !pip install --upgrade pip && pip install "numpy>=2.1,<3" "crewai>=0.51.0" "crewai_tools>=0.1.6" "langchain-community>=0.2.10"

# Warning control
import warnings
from crewai import Agent, Task, Crew
import os
from IPython.display import Markdown
from crewai_tools import ScrapeWebsiteTool
from datetime import datetime, timezone
from pathlib import Path
import uuid

warnings.filterwarnings("ignore")

ENV_OPENAI_API_KEY = "OPENAI_API_KEY"

def get_openai_api_key() -> str:
    """Return the OpenAI API key from the environment or raise with guidance."""
    api_key = os.getenv(ENV_OPENAI_API_KEY)
    if not api_key:
        raise RuntimeError(
            f"Missing {ENV_OPENAI_API_KEY}. Set it in your environment, e.g.,\n"
            f"export {ENV_OPENAI_API_KEY}='YOUR_KEY_HERE'"
        )
    return api_key

# Initialize environment and agent
openai_api_key = get_openai_api_key()
os.environ["OPENAI_MODEL_NAME"] = "gpt-3.5-turbo"


def save_output_markdown(content: str, *, outputs_dir: str = "outputs") -> str:
    """Save the given content as a Markdown file under `outputs/` with a unique ID.

    Returns the file path of the saved Markdown.
    """
    base = Path(outputs_dir)
    base.mkdir(parents=True, exist_ok=True)

    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    uid = uuid.uuid4().hex[:8]
    file_path = base / f"customer_support_{ts}_{uid}.md"

    header = (
        f"# Customer Support Response\n\n"
        f"Generated: {ts} UTC\n"
        f"Run ID: {uid}\n\n"
    )

    if not isinstance(content, str):
        content = str(content)

    file_path.write_text(header + content, encoding="utf-8")
    return str(file_path)

def create_support_agent(*, allow_delegation: bool = False, verbose: bool = True) -> Agent:
    """Create and configure the Support agent."""
    return Agent(
        role="Senior Support Representative",
        goal="Be the most friendly and helpful "
            "support representative in your team",
        backstory=(
            "You work at crewAI (https://crewai.com) and "
            "are now working on providing "
            "support to {customer}, a super important customer "
            "for your company. "
            "You need to make sure that you provide the best support! "
            "Make sure to provide full complete answers, "
            "and make no assumptions."
        ),
        allow_delegation=allow_delegation,
        verbose=verbose,
    )

def create_quality_assurance_agent(*, allow_delegation: bool = True, verbose: bool = True) -> Agent:
    """Create and configure the Quality Assurance agent."""
    return Agent(
        role="Support Quality Assurance Specialist",
        goal="Get recognition for providing the "
        "best support quality assurance in your team",
        backstory=(
            "You work at crewAI (https://crewai.com) and "
            "are now working with your team "
            "on a request from {customer} ensuring that "
            "the support representative is "
            "providing the best support possible.\n"
            "You need to make sure that the support representative "
            "is providing full"
            "complete answers, and make no assumptions."
        ),
        allow_delegation=allow_delegation,
        verbose=verbose,
    )

support_agent = create_support_agent()
# Important to set allow_delegation to True for QA agent.
qa_agent = create_quality_assurance_agent(allow_delegation=True)

def create_scrape_tool(*, url: str) -> ScrapeWebsiteTool:
    """Create and configure the Plan task."""
    return ScrapeWebsiteTool(website_url=url)

def create_inquiry_resolution_task(*, agent: Agent, tools) -> Task:
    """Create and configure the Inquiry Resolution task."""
    return Task(
        description=(
            "{customer} just reached out with a super important ask:\n"
            "{inquiry}\n\n"
            "{person} from {customer} is the one that reached out. "
            "Make sure to use everything you know "
            "to provide the best support possible."
            "You must strive to provide a complete "
            "and accurate response to the customer's inquiry."
        ),
        expected_output=(
            "A detailed, informative response to the "
            "customer's inquiry that addresses "
            "all aspects of their question.\n"
            "The response should include references "
            "to everything you used to find the answer, "
            "including external data or solutions. "
            "Ensure the answer is complete, "
            "leaving no questions unanswered, and maintain a helpful and friendly "
            "tone throughout."
        ),
        tools=tools,
        agent=agent,
    )

def create_quality_assurance_review_task(*, agent: Agent) -> Task:
    """Create and configure the Quality Assurance Review task."""
    return Task(
        description=(
            "Review the response drafted by the Senior Support Representative for {customer}'s inquiry. "
            "Ensure that the answer is comprehensive, accurate, and adheres to the "
            "high-quality standards expected for customer support.\n"
            "Verify that all parts of the customer's inquiry "
            "have been addressed "
            "thoroughly, with a helpful and friendly tone.\n"
            "Check for references and sources used to "
            " find the information, "
            "ensuring the response is well-supported and "
            "leaves no questions unanswered."
        ),
        expected_output=(
            "A final, detailed, and informative response "
            "ready to be sent to the customer.\n"
            "This response should fully address the "
            "customer's inquiry, incorporating all "
            "relevant feedback and improvements.\n"
            "Don't be too formal, we are a chill and cool company "
            "but maintain a professional and friendly tone throughout."
        ),
        agent=agent,
    )

scrape_tool = create_scrape_tool(url='https://docs.crewai.com/how-to/Creating-a-Crew-and-kick-it-off/')

inquiry_resolution = create_inquiry_resolution_task(agent=support_agent, tools=[scrape_tool])
quality_assurance_review = create_quality_assurance_review_task(agent=qa_agent)

crew = Crew(
  agents=[support_agent, qa_agent],
  tasks=[inquiry_resolution, quality_assurance_review],
  verbose=True,
  memory=True
)

inputs = {
    "customer": "DeepLearningAI",
    "person": "Andrew Ng",
    "inquiry": "I need help with setting up a Crew "
               "and kicking it off, specifically "
               "how can I add memory to my crew? "
               "Can you provide guidance?"
}

result = crew.kickoff(inputs=inputs)

output_path = save_output_markdown(getattr(result, "raw", str(result)))
print(f"Saved response to {output_path}")