import json

from openai import OpenAI

from selfImplemented.tools import code_writer, file_writer, test_writer
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
         Give your answer in the following format (while filling out the {} with your own input:
         
         STEP X:
         Explanation: {What needs to be done}
         Recommended Tool: {Your Tool Recommendation}
         Suggested Input: {Using the input parameters of the tool, determine the suggested input. If the input is
          dependent on the output of a previous step, write Output of Step Y}
          
        REMEMBER!, !each good code has to be saved, tested and also checked into git!, so make sure your plan includes 
         all those tasks and only references tools that are available to you, so no running of code. Your plan needs to include multiple steps
         """},

        {
            "role": "user",
            "content": "Write a a method that can add two numbers."
        }
    ]
)

thePlan = completionPlan.choices[0].message.content
print("########## THE PLAN ############ \n" + thePlan + "\n ############ END PLAN ########## \n")
executedSteps = "########## EXECUTED STEPS ############"
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
             Its format contains the order of the steps, an explanation of what needs to be done, a recommended tool,
             as well as the suggested input. The input can be given directly, or as the output of a previously executed step.
             The second message will contain a list of steps that we have already executed with its format containing
             the order of the steps, the tool that was used, the argument that was given and if applicable the generated output.
             This output might be needed to execute further steps later on
             If this list is empty, no steps have been executed until now.
             Compare the plan and the executed list with each other to determine the next step that needs to be executed. 
             Should you decide all steps of the plan have been executed (meaning you find a partner to all planned steps
             in the executed steps and at least more than one step was executed), output:
             
             STOP!
             
             Otherwise structure your output the following way:
             
             NEXT STEP:
             Recommended Tool: {Your Tool Recommendation}
             Input: {The input needed. Either determined by you, or use the output of a previous step}
             
             
             """},
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
    print("The next step: ", nextStep + "\n")
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
        arguments = json.loads(tool_call.function.arguments)
        print(arguments)
        executedSteps += "\n ****** EXECUTED STEP " + str(i+1) + " ******"
        if tool_call.function.name == "code_writer":
            executedSteps += "\n We used tool code_writer and generated code with following arguments:"
            executedSteps += "\n ARGUMENTS: " + arguments["request"]
            executedSteps += "\n OUTPUT OF STEP" + str(i) + "\n" + code_writer(arguments["request"]) + "\n END OUTPUT"
        if tool_call.function.name == "test_writer":
            executedSteps += "\n We used tool test_writer and generated tests with following arguments:"
            executedSteps += "\n ARGUMENTS: " + arguments["code"]
            executedSteps += "\n OUTPUT OF STEP" + str(i) + "\n" + test_writer(arguments["code"]) + "\n END OUTPUT"
        if tool_call.function.name == "fileWriter":
            executedSteps += "\n We used tool file_writer and saved the files:"
            executedSteps += ("\n ARGUMENTS: " + "content: "+ arguments["content"] + " | path: " +arguments["path"]
                              + " | fileType: " + arguments["fileType"])
            file_writer(arguments["content"], arguments["path"], arguments["fileType"])
        if tool_call.function.name == "git_commit":
            executedSteps += "We used tool git_commit to commit and push the code"
            executedSteps += "\n ********************"
    i += 1

print(executedSteps + "\n ############ END ##########")