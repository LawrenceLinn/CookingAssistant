from typing import Dict, List, Optional, Type
import os
from langchain.callbacks.manager import (
    AsyncCallbackManagerForToolRun,
    CallbackManagerForToolRun,
)
from langchain.pydantic_v1 import BaseModel, Field
from langchain.tools import BaseTool
import json
from langchain.agents import AgentExecutor
from langchain.agents.format_scratchpad import format_log_to_messages
from langchain.agents.output_parsers import (
    ReActJsonSingleInputOutputParser,
)
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.pydantic_v1 import BaseModel, Field
from langchain.schema import AIMessage, HumanMessage
from langchain.tools.render import render_text_description_and_args
from langchain_community.chat_models import ChatOllama
from langchain.prompts import MessagesPlaceholder
from typing import Tuple, List
from langchain_community.llms import Ollama


def get_preference_summary(
    ingredients: List[str],
    quantity: int,
    time: int,
    preference: List[str],
    tools: List[str],
    course: str,
    cuision: str,
) -> dict:
    summary = {
        "ingredients": ingredients,
        "quantity": quantity,
        "time": time,
        "preference": preference,
        "tools": tools,
        "course": course,
        "cuision": cuision,
    }
    return summary


def get_top3_recipes(summary: dict) -> List[tuple]:
    # TODO: replace with actual recommendation logic

    return [("Mushroom Risotto", 1), ("beef", 2), ("lamb", 3)]


all_cuisions = [
    "American",
    "Chinese",
    "French",
    "Indian",
    "Italian",
    "Japanese",
    "Mexican",
    "Thai",
    "Vietnamese",
]
all_courses = [
    "Appetizer",
    "Breakfast",
    "Brunch",
    "Dessert",
    "Dinner",
    "Lunch",
    "Main Course",
    "Side Dish",
    "Snack",
    "Starter",
]
all_preferences = [
    "Low-Carb",
    "Low-Fat",
    "High-Protein",
    "Spicy",
    "Sweet",
    "No-Spice",
    "No-Sugar",
]
all_tools = [
    "Blender",
    "Food Processor",
    "Grill",
    "Instant Pot",
    "Oven",
    "Pressure Cooker",
    "Slow Cooker",
    "Stove",
    "Wok",
]


class PreferenceSummarizationInput(BaseModel):
    ingredients: List[str] = Field(..., description="List of ingredients")
    quantity: Optional[int] = Field(
        default=1, description="Desired quantity. Default is 1 serving."
    )
    time: Optional[int] = Field(
        default=30, description="Maximum cooking time in minutes. eg.15, 30, 45, 60"
    )
    preference: Optional[List[str]] = Field(
        default=None,
        description="Meal preferences. Available options are:" f"{all_preferences}",
    )
    tools: Optional[List[str]] = Field(
        None,
        description="Required kitchen tools. Available options are:" f"{all_tools}",
    )
    course: Optional[str] = Field(
        None, description="Course type. Available options are:" f"{all_courses}"
    )
    cuision: Optional[str] = Field(
        None, description="Cuisine type. Available options are:" f"{all_cuisions}"
    )


class PreferenceSummarizationTool(BaseTool):
    name = "PreferenceSummarization"
    description = "Summarize or update human's cooking preferences. After action, you should ask human for feedback."
    args_schema: Type[BaseModel] = PreferenceSummarizationInput

    def _run(
        self,
        ingredients: List[str] = ...,
        quantity: Optional[int] = 1,
        time: Optional[int] = 30,
        preference: Optional[List[str]] = None,
        tools: Optional[List[str]] = None,
        course: Optional[str] = None,
        cuision: Optional[str] = None,
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> str:
        """Use the tool."""
        summary = get_preference_summary(
            ingredients, quantity, time, preference, tools, course, cuision
        )
        top3_recipes = get_top3_recipes(summary)
        # print(ingredients, quantity, time, preference, tools)
        output = f"This is the prefernce summary from user: {json.dumps(summary)}.\n And the top 3 recommending recipe:{top3_recipes}\n"
        # user_response = input()
        return output

    async def _arun(
        self,
        ingredients: List[str],
        quantity: Optional[int] = 1,
        time: Optional[int] = 30,
        preference: Optional[List[str]] = None,
        tools: Optional[List[str]] = None,
        course: Optional[str] = None,
        cuision: Optional[str] = None,
        run_manager: Optional[AsyncCallbackManagerForToolRun] = None,
    ) -> str:
        """Use the tool asynchronously."""
        summary = get_preference_summary(
            ingredients, quantity, time, preference, tools, course, cuision
        )
        top3_recipes = get_top3_recipes(summary)
        # print(ingredients, quantity, time, preference, tools)
        output = f"This is the prefernce summary from user: {json.dumps(summary)}.\n And the top 3 recommending recipe:{top3_recipes}\n"
        return output


llm = Ollama(model="mixtral:8x7b-instruct-v0.1-q2_K", base_url="http://ollama:11434")
tools = [PreferenceSummarizationTool()]
chat_model_with_stop = llm.bind(stop=["\nObservation"])

# Inspiration taken from hub.pull("hwchase17/react-json")
"""As a Recipe Recommendation Bot, your purpose is to suggest cooking recipes to users based on the ingredients they have and their cooking preferences. 
When users provide you with a list of ingredients and any specific tastes or dietary requirements, 
you'll match these criteria with your comprehensive recipe database to recommend the three most similar dishes using the Retrieval-Augmented Generation (RAG) approach. 
If the user wants to adjust their preferences or learn more about a specific dish, they can do so. 
On selecting a dish, you'll summarize the recipe, including steps, 
tips, missing ingredients, and nutritional information, 
ensuring a seamless and informative cooking experience."""
system_message = f"""
You are a chatbot that helps users find recipes based on their preferences.
Answer the user's questions and provide them with the information they need.
You can answer directly if the user is greeting you or similar.
Otherise, you have access to the following tools:

{render_text_description_and_args(tools).replace('{', '{{').replace('}', '}}')}

The way you use the tools is by specifying a json blob.
Specifically, this json should have a `action` key (with the name of the tool to use)
and a `action_input` key (with the input to the tool going here).
The only values that should be in the "action" field are: {[t.name for t in tools]}
The $JSON_BLOB should only contain a SINGLE action, 
do NOT return a list of multiple actions.
Here is an example of a valid $JSON_BLOB:
```
{{{{
    "action": $TOOL_NAME,
    "action_input": $INPUT
}}}}
```
The $JSON_BLOB must always be enclosed with triple backticks!

ALWAYS use the following format:
Question: the input question you must answer
Thought: you should always think about what to do
Action:
```
$JSON_BLOB
```

Observation: the result of the action... 

Final Answer: the final answer based on the result of the action

Begin! Reminder to always use the exact characters `Final Answer` when responding.'
"""
#
# Thought: I now know the final answer
# (this Thought/Action/Observation can repeat N times)
prompt = ChatPromptTemplate.from_messages(
    [
        (
            "user",
            system_message,
        ),
        MessagesPlaceholder(variable_name="chat_history"),
        ("user", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ]
)


def _format_chat_history(chat_history: List[Tuple[str, str]]):
    buffer = []
    for human, ai in chat_history:
        buffer.append(HumanMessage(content=human))
        buffer.append(AIMessage(content=ai))
    return buffer


agent = (
    {
        "input": lambda x: x["input"],
        "agent_scratchpad": lambda x: format_log_to_messages(x["intermediate_steps"]),
        "chat_history": lambda x: _format_chat_history(x["chat_history"]),
    }
    | prompt
    | chat_model_with_stop
    | ReActJsonSingleInputOutputParser()
)


# Add typing for input
class AgentInput(BaseModel):
    input: str
    chat_history: List[Tuple[str, str]] = Field(
        ..., extra={"widget": {"type": "chat", "input": "input", "output": "output"}}
    )
    # agent_scratchpad: List[str] = Field(
    #     ..., extra={"widget": {"type": "scratchpad", "input": "input", "output": "output"}}
    # )


class AgentOutput(BaseModel):
    output: str
    chat_history: List[Tuple[str, str]] = Field(
        ..., extra={"widget": {"type": "chat", "input": "input", "output": "output"}}
    )
    agent_scratchpad: List[str] = Field(
        ...,
        extra={"widget": {"type": "scratchpad", "input": "input", "output": "output"}},
    )


def create_agent_executor():
    return AgentExecutor(
        agent=agent,
        tools=tools,
        verbose=True,
        return_intermediate_steps=True,
        handle_parsing_errors=True,
        return_scratchpad=True,
        max_iterations=5,
    ).with_types(input_type=AgentInput, output_type=AgentOutput)
