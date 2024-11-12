from langchain_core.messages import SystemMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, HumanMessagePromptTemplate
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from pydantic import BaseModel, Field
from langchain import hub
from langchain.agents import AgentExecutor, create_tool_calling_agent


class CodeRequest(BaseModel):
    request: str = Field(description="Describe in !natural language!, what code I should write")

class UnitTestRequest(BaseModel):
    code: str = Field(description="Give me code, I will write a unit tests")

@tool(args_schema=CodeRequest)
def write_code(request: str) -> str:
    """Can write python code"""
    coder = ChatOpenAI()
    coder_output = StrOutputParser()
    code_chain = coder | coder_output

    coder_template = ChatPromptTemplate.from_messages([
        SystemMessage(content="You are a python programmer tasked with helping the human. If asked for writing code, always provide only the code, no annotations around it"),
        HumanMessagePromptTemplate.from_template("{text}")
    ])
    return code_chain.invoke(coder_template.format_messages(text=request))

@tool(args_schema=UnitTestRequest)
def unit_tester(code: str) -> str:
    """Can write python code"""
    coder = ChatOpenAI()
    coder_output = StrOutputParser()
    code_chain = coder | coder_output

    coder_template = ChatPromptTemplate.from_messages([
        SystemMessage(content="You are a python programmer tasked with helping the human. Your input will be python code and your task is to write as many unit tests for it, as you think are needed. In the answer always provide only the code, no annotations around it"),
        HumanMessagePromptTemplate.from_template("{text}")
    ])
    return code_chain.invoke(coder_template.format_messages(text=code))


# Get the prompt to use - you can modify this!
prompt = hub.pull("hwchase17/openai-tools-agent")
prompt.pretty_print()

tools = [write_code, unit_tester]
llm = ChatOpenAI()

llm_with_tools = llm.bind_tools([write_code, unit_tester])
output_parser = StrOutputParser()
messages = [ ("system", "You are an AI Agent, you shall distribute all tasks to tools. You do not answer user requests yourself! Remember, every code needs to be tested"),
             ("human", "Please write a method that adds two numbers")
             ]
#result = llm_with_tools.invoke(messages)
#tool_call = result.tool_calls[0]
#selected_tool = {"write_code": write_code, "unit_tester": unit_tester}[tool_call["name"].lower()]
#chain = selected_tool | output_parser
#print(chain.invoke(tool_call["args"]))

agent = create_tool_calling_agent(llm, tools, prompt)
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)
agent_executor.invoke({
    "input": "Please write a method that adds two numbers and also test the code"
})