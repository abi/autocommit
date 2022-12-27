import os
import re
import markdown

from pydantic import BaseModel
from langchain.llms import OpenAI
from langchain.prompts import BasePromptTemplate
from dotenv import load_dotenv

load_dotenv()

OPENAI_KEY = os.getenv("OPENAI_KEY")


class CustomPromptTemplate(BasePromptTemplate, BaseModel):
    template: str

    def format(self, **kwargs) -> str:
        c_kwargs = {k: v for k, v in kwargs.items()}
        return self.template.format(**c_kwargs)


prompt = CustomPromptTemplate(
    input_variables=["diff"], template="""
    What follows "-------" is a git diff for a potential commit.
    Reply with a markdown unordered list of 5 possible, different Git commit messages 
    (a Git commit message should be concise but also try to describe 
    the important changes in the commit), order the list by what you think 
    would be the best commit message first, and don't include any other text 
    but the 5 messages in your response.
    ------- 
    {diff}
    -------
""")


def generate_suggestions(diff, openai_api_key=OPENAI_KEY):

    llm = OpenAI(temperature=0.2, openai_api_key=openai_api_key,
                 max_tokens=100, model_name="text-davinci-003")  # type: ignore

    # query OpenAI
    formattedPrompt = prompt.format(diff=diff)
    response = llm(formattedPrompt)

    # Convert the markdown string to HTML
    html = markdown.markdown(response)

    # Use a regular expression to extract the list items from the HTML
    items = re.findall(r'<li>(.*?)</li>', html)
    return items
