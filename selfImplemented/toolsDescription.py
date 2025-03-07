programmerTool = {
    "type": "function",
    "function": {
        "name": "code_writer",
        "description": "When given the description of a desired method, I will write the code for it",
        "parameters": {
            "type": "object",
            "properties": {
                "request": {
                    "type": "string",
                    "description": """The description of the method given in natural language, 
                    as described by a person who can not code""",
                },
            },
            "required": ["request"],
            "additionalProperties": False,
        }
    }
}

testerTool = {
    "type": "function",
    "function": {
        "name": "test_writer",
        "description": "Given the code of a python method, I will write unit tests for it",
        "parameters": {
            "type": "object",
            "properties": {
                "code": {
                    "type": "string",
                    "description": """The python code that needs to be tested""",
                },
            },
            "required": ["code"],
            "additionalProperties": False,
        }
    }
}

fileWriterTool = {
    "type": "function",
    "function": {
        "name": "fileWriter",
        "description": "Given any string, I will write it to the filesystem",
        "parameters": {
            "type": "object",
            "properties": {
                "fileName": {
                    "type": "string",
                    "description": """The name of the file""",
                },
                "fileType": {
                    "type": "string",
                    "description": """The type of the file, determines the suffix of the filename""",
                },
                "content": {
                    "type": "string",
                    "description": """The content of the file. This is what will be saved""",
                },
            },
            "required": ["content"],
            "additionalProperties": False,
        }
    }
}

commitTool = {
    "type": "function",
    "function": {
        "name": "git_commit",
        "description": "I will commit written files",
    }
}