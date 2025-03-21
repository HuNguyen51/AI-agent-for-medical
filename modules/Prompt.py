from langchain.prompts import PromptTemplate

class Prompt(PromptTemplate):
    def __init__(self, template, input_variables):
        super().__init__(template = template, input_variables=input_variables)