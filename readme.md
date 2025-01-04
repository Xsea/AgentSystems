This project contains a small demo of LLM Agent systems.

To run it following install following packages:

```pip install openai```

and then follow the setup in: https://platform.openai.com/docs/quickstart

Additionally, if you want the code to automatically commit and push to git, you need to have setup a git repository, 
as well as install:

```pip install gitpython```

Otherwise, delete line 120 "git_push()" of selfImplementedAgent.py, the LLM will tell you it used the function, but no 
code was executed.

Lastly following variables in tools.py need to be set to run properly:

PATH_WHERE_GENERATED_CODE_GOES and PATH_OF_GIT_REPO, COMMIT_MESSAGE if you want the git push functionality

For now, only the self implemented part (without Langchain) is running. Execute selfImplementedAgent.py for the demo