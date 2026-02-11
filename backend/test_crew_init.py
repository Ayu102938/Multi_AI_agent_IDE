import os
from dotenv import load_dotenv
from crewai import Agent, Crew, Task, Process
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()

# Ensure no OPENAI_API_KEY is detected in env for this test
os.environ["OPENAI_API_KEY"] = "sk-dummy-key-to-bypass-check"

print("Testing CrewAI Agent initialization with Gemini and memory=False...")

api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    print("GOOGLE_API_KEY not found in env.")
    exit(1)

try:
    # Use LiteLLM string format
    llm = "gemini/gemini-flash-latest"
    print("LLM string set.")

    agent = Agent(
        role="TestAgent",
        goal="Test initialization",
        backstory="I am a test.",
        llm=llm,
        # function_calling_llm=llm, # LiteLLM might handle this automatically or via same string
        memory=False
    )
    print("Agent initialized.")

    task = Task(
        description="Say hello",
        expected_output="Hello",
        agent=agent
    )
    
    crew = Crew(
        agents=[agent],
        tasks=[task],
        verbose=True,
        memory=False
    )
    print("Crew initialized. Kickoff...")
    
    crew.kickoff()
    print("Success!")

except Exception as e:
    print(f"FAILED with error: {e}")
    import traceback
    traceback.print_exc()
