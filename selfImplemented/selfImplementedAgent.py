import json

from openai import OpenAI
from toolsDescription import programmerTool, testerTool, fileWriterTool, commitTool
client = OpenAI()

tools = [programmerTool, testerTool, fileWriterTool, commitTool]

completionPlan = client.chat.completions.create(
    model="gpt-4o-mini",
    tools=tools,
    messages=[
        {"role": "system",
         "content": """You are a python programming agent  has to determine how to solve a task given by the user. 
         You do not solve tasks yourself, but only determine the step by step plan given your accessible tools.
         Each step should include the tool you need as well as their input needed.
         Remember, each good code has to be saved, tested and also checked into git"""},
        {
            "role": "user",
            "content": "Write a a method that can add two numbers."
        }
    ]
)

thePlan = completionPlan.choices[0].message.content
executedSteps = "Steps that were already executed:"
nextStep = ""
i = 0
while nextStep != "STOP!" and i < 10:
    completionStep = client.chat.completions.create(
        model="gpt-4o-mini",
        tools=tools,
        tool_choice='none',
        messages=[
            {"role": "system",
             "content": """The next message you will receive is a step by step plan of a task we need to execute.
             The second message will contain a list of task that we have already executed as well as some details to the
             execution. If this list is empty, no tasks have been executed until now.
             Compare the plan and the executed list with each other to determine the next step 
             that needs to be executed. If all steps are done, write "STOP!"
             Your output will be given to an llm, that will determine which tool should be used for executing the next step.
             Please write accordingly an instruction in natural language"""},
            {
                "role": "system",
                "content": thePlan
            },
            {
                "role": "system",
                "content": executedSteps
            }
        ]
    )
    nextStep = completionStep.choices[0].message.content
    print("The next step: ", nextStep)
    if nextStep == "STOP!":
        break

    completionTool = client.chat.completions.create(
        model="gpt-4o-mini",
        tools=tools,
        tool_choice='required',
        messages=[
            {"role": "system",
             "content": """Read the assistant message below and determine which tool to use to satisfy this task"""},
            {
                "role": "assistant",
                "content": nextStep
            }
        ]
    )

    if completionTool.choices[0].finish_reason == 'tool_calls':
        tool_call = completionTool.choices[0].message.tool_calls[0]
        if tool_call.function.name == "code_writer":
            executedSteps += "\n We wrote code according to following description:"
            executedSteps += "\n " + tool_call.function.arguments
        if tool_call.function.name == "test_writer":
            executedSteps += "\n We wrote tests according to following description:"
            executedSteps += "\n " + tool_call.function.arguments
        if tool_call.function.name == "fileWriter":
            executedSteps += "\n We saved a file to following location:"
            executedSteps += "\n " + tool_call.function.arguments
        if tool_call.function.name == "fileWriter":
            executedSteps += "\n We commited and pushed code"
    i += 1

print(executedSteps)