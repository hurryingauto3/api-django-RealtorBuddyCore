# Path: twilioService/llm_utils.py
import json
import logging

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from langchain.output_parsers import PydanticOutputParser
from langchain.prompts import PromptTemplate
from langchain_core.pydantic_v1 import BaseModel, Field, validator

logger = logging.getLogger(__name__)


# Function to distill the name of the building/address from the customer's search query
def distillSearchItemFromQuery(search_query: str) -> str:
    """
    Function to distill the name of the building/address from the customer's search query
    """
    if not search_query:
        return None

    class SearchQuery(BaseModel):
        search_query: str = Field(
            description="The name of the building/address from the customer's search query"
        )

        @validator("search_query")
        def validate_search_query(cls, value):
            if not value:
                raise ValueError("Search query cannot be empty")
            return value

    parser = PydanticOutputParser(pydantic_object=SearchQuery)
    llm = ChatOpenAI(model="gpt-4")
    query = f'Extract the name of the building/address from the search query: "{search_query}"'
    prompt = PromptTemplate(
        template="\n{format_instructions}\n{query}\n",
        input_variables=["query"],
        partial_variables={"format_instructions": parser.get_format_instructions()},
    )
    _input = prompt.format_prompt(query=query)
    input_string = _input.to_string()
    messages = [
        HumanMessage(content=(input_string)),
    ]
    retries = 3
    # logger.info("input_string: %s", input_string)ß
    for retry in range(retries):
        try:
            output = llm.invoke(messages)
            output_json = json.loads(output.content)
            return output_json.get("search_query")
        except Exception as e:
            logger.error("Error generating client requirements: %s", e)
            logger.error("Retrying...{}/{}".format(retry + 1, retries))

    return None


# Function to output the search results to the customer in a user-friendly format
def displaySearchResultsToCustomer(user_query, search_results) -> str:
    """
    Function to output the search results to the customer in a user-friendly format
    """
    
    if not user_query:
        return None

    class clientReply(BaseModel):
        client_reply: str = Field(
            description="The search results to be displayed to the customer"
        )

        @validator("client_reply")
        def validate_client_reply(cls, value):
            if not value:
                raise ValueError("Client reply cannot be empty")
            return value

    parser = PydanticOutputParser(pydantic_object=clientReply)
    llm = ChatOpenAI(model="gpt-4")
    query = f"""
    You are John, an agent that is responsible for helping locators/realtors/real estate professionals find out if a certain property cooperates with them and on what terms. You have access to do perform an api call to retrieve this information. The client may make an ask of you in the following ways:

    'Hey John, can you tell me if Gallaries at Park Lane cooperates?"
    "Hi, does 2801 Broadmead Dr, Houston pay locators"
    "Can you tell me if  [building name] cooperates?"

    Generally the ask will include a building name and/or a building address as the main identifier of the building in question that needs its cooperating status clarified.

    Please output this information in the following format:

    IF the building cooperates:

    "Hey, the [building name requested] cooperates at [insert cooperation percentage]. It's located at [address], and our last update for this is [last update timestamp (date only)]. Feel free to ask us anything else!"

    IF the building does not cooperate:

    "Hey this building does not cooperate with locators at the moment. We checked this last at [last update timestamp]. Do you have other buildings we can try to place at?"
    
    These are the search results for the query: "{user_query}"
    
    {search_results}
    """
    prompt = PromptTemplate(
        template="\n{format_instructions}\n{query}\n",
        input_variables=["query"],
        partial_variables={"format_instructions": parser.get_format_instructions()},
    )
    _input = prompt.format_prompt(query=query)
    input_string = _input.to_string()
    messages = [
        SystemMessage(content=(input_string)),
        HumanMessage(content=(user_query)),
    ]
    retries = 3
    for retry in range(retries):
        try:
            output = llm.invoke(messages)
            output_json = json.loads(output.content)
            return output_json.get("client_reply")
        except Exception as e:
            logger.error("Error generating client requirements: %s", e)
            logger.error("Retrying...%s/%s", retry + 1, retries)

    return None
