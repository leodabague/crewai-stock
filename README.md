# AI-Agent Crew for Stock Analysis | WIP

Experimental and educational-aimed project using:
1. CrewAI | AI-Agent Framework
2. Streamlit | Visual Framework
3. Annotated-text | Enriched text
4. LLM (gpt4o-mini)
5. Serper.Dev | Search engine API

--

As Input the user sents a stock Ticker and receives a report on the latest news of a stock: both .md file and on screen.

## Instructions
pre-req: python, pip

Install crewai:
pip install crewai

Setup the base crew:
crewai create crew [name-of-the-crew]

Insert the streamlit python file in the root folder of your crew.
Create a .env file and update it with your credentials (openAI + serperdev)

Modify:
- main.py
- crew.py

And also the agents descriptions and task descriptions.
