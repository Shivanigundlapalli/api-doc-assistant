
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.prebuilt import create_react_agent
from langchain_core.tools import Tool
from dotenv import load_dotenv
load_dotenv()
def calculate(expression: str): return str(eval(expression))
tools = [Tool.from_function(func=calculate, name='calculator', description='calculate')]
llm = ChatGoogleGenerativeAI(model='gemini-1.5-pro')
agent = create_react_agent(llm, tools)
for chunk in agent.stream({'messages': [('user', 'What is 2+2?')] }):
    print(chunk)

