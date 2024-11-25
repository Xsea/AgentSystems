import os

from exceptiongroup import catch
from openai import OpenAI

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

def file_writer(content, path, type):
    file_name = path
    save_type = ""
    if path[-2:] != "py" and (type == "python" or type == "py"):
        save_type = ".py"
    file_name += save_type
    files = os.listdir("../generatedCode")
    while file_name in files:
        file_name = file_name[0:-3] +"copy" + save_type
    f = open("../generatedCode/"+file_name, "x")
    f.write(content)
    f.close()
    return "../generatedCode/"+file_name