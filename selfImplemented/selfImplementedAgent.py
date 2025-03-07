import json
from dataclasses import asdict

from openai import OpenAI
from selfImplemented.tools import code_writer, file_writer, test_writer, git_push
from toolsDescription import programmerTool, testerTool, fileWriterTool, commitTool

client = OpenAI()

########## PLANNING ##########
def planning(user_request):
    # read user input and devise a plan on how to solve it
    completion_plan = client.chat.completions.create(
        model="gpt-4o",
        tools=tools,
        messages=[
            {"role": "system",
             "content": """You are a python programming agent who has to determine how to solve a task given by the user. 
             You do not solve tasks yourself, but only determine the step by step plan given your accessible tools.
             Give your answer in the following format (while filling out the {} with your own input:
             
             STEP X:
             Explanation: {What needs to be done}
             Recommended Tool: {Your Tool Recommendation}
             Suggested Input: {Using the input parameters of the tool, determine the suggested input. If the input is
              dependent on the output of a previous step, write Output of Step Y}
              
            REMEMBER!, !each good code has to be saved, tested and also checked into git!, so make sure your plan includes 
             all those tasks and only references tools that are available to you, so no running of code. 
             You do not have parallel tool capability. Your plan needs to include multiple steps
             """},

            {
                "role": "user",
                "content": user_request
            }
        ]
    )

    return completion_plan.choices[0].message.content

########## END PLANNING ##########

########## MEMORY ##########
def memory(tool_name, arguments, output, step):
    # explain what happened in this step, so that the llm knows can decide the next step
    executed_step = "\n ****** EXECUTED STEP " + str(step+1) + " ******"
    if tool_name == "code_writer":
        executed_step += "\n We used tool code_writer and generated code with following arguments:"
        executed_step += "\n ARGUMENTS: " + arguments["request"]
        executed_step += "\n OUTPUT OF STEP" + str(step) + "\n" + output + "\n END OUTPUT"
    elif tool_name == "test_writer":
        executed_step += "\n We used tool test_writer and generated tests with following arguments:"
        executed_step += "\n ARGUMENTS: " + arguments["code"]
        executed_step += "\n OUTPUT OF STEP" + str(step) + "\n" + output + "\n END OUTPUT"
    elif tool_name == "fileWriter":
        executed_step += "\n We used tool file_writer and saved the files:"
        executed_step += ("\n ARGUMENTS: " + "content: "+ arguments["content"] + " | name: " +arguments["fileName"]
                          + " | fileType: " + arguments["fileType"])
    elif tool_name == "git_commit":
        executed_step += "We used tool git_commit to commit and push the code"
        executed_step += "\n ********************"
    return executed_step
########## END MEMORY ##########

##########   TOOLS    ##########
# which tools does our LLM have access to
tools = [programmerTool, testerTool, fileWriterTool, commitTool]
########## END TOOLS ###########

def main():
    user_request = str(input("How can I help you? \n"))
    the_plan = planning(user_request)
    print("########## THE PLAN ############ \n" + the_plan + "\n ############ END PLAN ########## \n")

    executed_steps = "########## EXECUTED STEPS ############"
    i = 0
    while i < 20:
        print("########### STEP {0} ######################".format(i+1))
        # we start by analyzing the plan and the executed steps -> this will determine the next step
        completion_step = client.chat.completions.create(
            model="gpt-4o",
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
                 Remember, that you have not parallel tool use capability.
                 Please output your suggestion for a next step in the following valid JSON format with the following way 
                 (Read the Text between $$ as explanations of the parameter):
                 {
                    "chainOfThoughts": $Your chain of thoughts while solving this tasks. Fill it with your reasoning$
                    "nextStep": $leave this object null if no step is needed$ {
                        "recommendedTool": $Your tool recommendation. To determine this look at your available tools$
                        "Input": $The input needed. Either determined by you, or use the output of a previous step$
                    }
                    "finish": $Boolean parameter, fill with false if you determine there is a next step, true if you determine the task is solved
                 }
                 """},
                {
                    "role": "system",
                    "content": the_plan
                },
                {
                    "role": "system",
                    "content": executed_steps
                }
            ]
        )
        next_step = completion_step.choices[0].message.content
        print("########## WE WILL DO THE FOLLOWING: \n", next_step + "\n############\n")

        # sometimes the LLM creates a valid json, but starts with the annotation ```json then {} and ends with ```
        next_step = next_step.removeprefix("```json").removesuffix("```")
        next_step_parsed = json.loads(next_step)

        # we are done - lets get out
        if next_step_parsed["finish"]:
            break

        # now we use the determined next plan and execute the tool - needs separation as text generation and tool call can
        # not be done simultaneously
        completion_tool = client.chat.completions.create(
            model="gpt-4o-mini",
            tools=tools,
            tool_choice='required',
            messages=[
                {"role": "system",
                 "content": """Read the assistant message below and determine which tool to use to satisfy this task"""},
                {
                    "role": "assistant",
                    "content": str(next_step_parsed["nextStep"])
                }
            ]
        )

        # save what we have done - this is our short term memory.
        # The LLM will use this to determine what has been done and what needs to be done next
        if completion_tool.choices[0].finish_reason == 'tool_calls':
            tool_call = completion_tool.choices[0].message.tool_calls[0]
            arguments = json.loads(tool_call.function.arguments)
            output = ""
            if tool_call.function.name == "code_writer":
                output = code_writer(arguments["request"])
            if tool_call.function.name == "test_writer":
                output = test_writer(arguments["code"])
            if tool_call.function.name == "fileWriter":
                file_writer(arguments["content"], arguments["fileName"], arguments["fileType"])
            if tool_call.function.name == "git_commit":
                git_push()
            this_step = memory(tool_call.function.name, arguments, output, i)
            print(this_step)
            executed_steps += this_step
        i += 1

main()