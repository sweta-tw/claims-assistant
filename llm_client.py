from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()


class LLMClient:

    def __init__(self):
        self.client = OpenAI()

    def chat(self, input, tools=None):

        response = self.client.responses.create(
            model="gpt-5-nano",
            input=input,
            tools=tools
        )

        return response