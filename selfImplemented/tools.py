import os
from openai import OpenAI
from git import Repo

PATH_WHERE_GENERATED_CODE_GOES = "../../GeneratedCode/"
PATH_OF_GIT_REPO = r'../../GeneratedCode/.git'  # make sure .git folder is properly configured
COMMIT_MESSAGE = 'auto generated code'

def code_writer(description):
    client = OpenAI()
    code_writer_completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system",
             "content": """You write python code according to the description given to you. Please read the next message
             and write according code. In your output, only write the code! No instructions or explanations before or after.
             If you feel these are necessary, add them as comments to the code"""},
            {
                "role": "system",
                "content": description
            }
        ]
    )
    return code_writer_completion.choices[0].message.content

def test_writer(code):
    client = OpenAI()
    test_writer_completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system",
             "content": """Given the code in the next message, write test code containing all tests you feel are needed
             to test this code satisfactorily. In your output, only write the code! No instructions or explanations before or after.
             If you feel these are necessary, add them as comments to the code"""},
            {
                "role": "system",
                "content": code
            }
        ]
    )
    return test_writer_completion.choices[0].message.content

def file_writer(content, path, file_type):
    file_name = path
    save_type = ""
    if path[-2:] != "py" and (file_type == "python" or file_type == "py"):
        save_type = ".py"
    file_name += save_type
    files = os.listdir(PATH_WHERE_GENERATED_CODE_GOES)
    while file_name in files:
        file_name = file_name[0:-3] +"copy" + save_type
    f = open(PATH_WHERE_GENERATED_CODE_GOES+file_name, "x")
    f.write(content)
    f.close()
    return PATH_WHERE_GENERATED_CODE_GOES+file_name

def git_push():
    try:
        print("trying")
        repo = Repo(PATH_OF_GIT_REPO)
        repo.git.add(".")
        repo.index.commit(COMMIT_MESSAGE)
        origin = repo.remote(name='origin')
        origin.push()
        print("done")
    except:
        print('Some error occured while pushing the code')
