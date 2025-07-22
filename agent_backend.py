from agents import Agent, Runner
from dotenv import load_dotenv
from pydantic import BaseModel
import openai
import os

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY_spanish_teacher")
openai.api_key = api_key


class Translations(BaseModel):
    user_spanish_transcript: str
    english_translation_of_user_spanish_transcript: str
    corrected_user_spanish_transcript: str
    correctness_score_of_user_spanish_transcript: float
    spanish_agent_response: str
    english_translation_of_spanish_agent_response: str


@function_tool
def covert_text_to_speech(city: str) -> str:
    print(f"Getting weather for {city}")
    return f"Weather's good"
