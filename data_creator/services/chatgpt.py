from agents import Agent, Runner
from pydantic import BaseModel
import asyncio

class TextNetlistPair(BaseModel):
    text: str
    netlist: str

class TextToNetlistOutput(BaseModel):
    pairs: list[TextNetlistPair]

class ChatGPTService:
    agent = Agent(
        name="Assistant",
        instructions="You are an expert in transforming text to NETLIST CODE. The user will ask you to generate examples of text-netlist code pairs. You will have to imagine a text description of an electrical circuit and generate the corresponding netlist code. You will have to generate as many examples as the user asks you to.",
        output_type=TextToNetlistOutput,
        model="gpt-4o-mini",
    )

    async def generate_response(self, nb_results: int) -> TextToNetlistOutput:
        print(f"Generating {nb_results} text-netlist code pairs...")

        result = await Runner.run(
            self.agent,
            'Generate {nb_results} examples of text descriptions and their corresponding netlist code.'
        )

        print("Generated response:", result.final_output)

        return result.final_output