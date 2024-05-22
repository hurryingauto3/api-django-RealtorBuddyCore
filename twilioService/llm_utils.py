# Path: twilioService/llm_utils.py
import json
import logging
import requests
import datetime

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from langchain.output_parsers import PydanticOutputParser
from langchain.prompts import PromptTemplate
from langchain_core.pydantic_v1 import BaseModel, Field, validator

from slackService.utils import validateBuildingDataFromSlack

logger = logging.getLogger(__name__)

extraction_llm = "gpt-3.5-turbo"
presentation_llm = (
    "gpt-3.5-turbo"  # LLM being used for outputting the search results to the customer
)


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

        @validator("search_query", allow_reuse=True)
        def validate_search_query(cls, value):
            if not value:
                raise ValueError("Search query cannot be empty")
            return value

    parser = PydanticOutputParser(pydantic_object=SearchQuery)
    llm = ChatOpenAI(model=extraction_llm)
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
    retries = 1
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
def generateRelevantBuildingData(user_query, search_results) -> int:
    """
    Function to output the search results to the customer in a user-friendly format
    """

    if not user_query:
        return None

    class clientReply(BaseModel):
        client_reply: str = Field(
            description="The search results to be displayed to the customer"
        )

        @validator("client_reply", allow_reuse=True)
        def validate_client_reply(cls, value):
            if not value:
                raise ValueError("Client reply cannot be empty")
            return value

    class buildingID(BaseModel):
        building_id: int = Field(
            description="The building ID of the relevant building from the given results"
        )

        @validator("building_id", allow_reuse=True)
        def validate_building_id(cls, value):
            if not value:
                raise ValueError("Building ID cannot be empty")
            return value

    # parser = PydanticOutputParser(pydantic_object=clientReply)
    parser = PydanticOutputParser(pydantic_object=buildingID)
    llm = ChatOpenAI(model=presentation_llm)
    # System pr
    query = f"""
    You are John, an agent that is responsible for helping locators/realtors/real estate professionals discover if a certain property cooperates with them and on what terms. You have access to perform an api call to retrieve this information. The client may make an ask of you in the following ways:

    'Hey John, can you tell me if Gallaries at Park Lane cooperates?"
    "Hi, does 2801 Broadmead Dr, Houston pay locators"
    "Can you tell me if  [building name] cooperates?"

    Generally the ask will include a building name and/or a building address as the main identifier of the building in question that needs its cooperating status clarified. The results will be presented to you in the following format: "{user_query}"
    
    You must interpret the results and make a reasonable estimate of which one of the results is the building name/address that the client is asking about.
    
    Return the correct building id as json    
      
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
        # HumanMessage(content=(user_query)),
    ]

    retries = 3
    for retry in range(retries):
        try:
            output = llm.invoke(messages)
            output_json = json.loads(output.content)
            # return output_json.get("client_reply")
            return output_json.get("building_id")
        except Exception as e:
            logger.error("Error generating client requirements: %s", e)
            logger.error("Retrying...%s/%s", retry + 1, retries)

    return None


def get_building_data(building_id):
    """Fetch building data from the API."""
    response = requests.get(
        f"http://127.0.0.1:8000/buildings/api/{building_id}/?format=json"
    )
    if response.status_code == 200:
        return response.json()
    else:
        logger.error(
            f"Failed to fetch building data for ID {building_id}, status code {response.status_code}"
        )
        return None


def format_date(date_string):
    """Convert ISO datetime string to formatted date."""
    date_only = date_string.split("T")[0]
    return datetime.datetime.strptime(date_only, "%Y-%m-%d").date()


def get_cooperation_message(
    building_name,
    cooperation,
    cooperation_percentage,
    address,
    last_update,
    needs_update,
):
    """Generate the cooperation status message based on the building data."""
    update_message = (
        " We'll confirm again and let you know if anything's changed. "
        if needs_update
        else ""
    )
    if cooperation:
        cooperation_text = (
            f"cooperates at {cooperation_percentage}%"
            if cooperation_percentage
            else "cooperates"
        )
        update_message = (
            " We'll get back to you with the cooperation percentage soon. "
            if not cooperation_percentage
            else update_message
        )
        return f"Hey, the {building_name} {cooperation_text}. It's located at {address}, and our last update for this is {last_update}.{update_message} Feel free to ask us anything else!"
    else:
        return f"Hey, this building does not cooperate with locators at the moment. We checked this last at {last_update}.{update_message} Do you have other buildings you'd like us to check?"


def displaySearchResultsToCustomer(user_query, search_results, from_number):
    building_id = generateRelevantBuildingData(user_query, search_results)

    building_data = get_building_data(building_id)
    if not building_data:
        return "We're having trouble retrieving the building details right now. Please try again later."

    building_name = building_data.get("name")
    address = building_data.get("address")
    last_update = format_date(building_data["updated_at"])

    cooperation_info = building_data.get("cooperation", [{}])[0]
    cooperation = cooperation_info.get("cooperate")
    cooperation_percentage = cooperation_info.get("cooperation_percentage")

    needs_update = False
    # Check if the data is older than 30 days to validate from slack
    if datetime.datetime.now().date() - last_update > datetime.timedelta(days=15):
        validateBuildingDataFromSlack(
            building_id, building_name, user_query, from_number
        )
        needs_update = True

    return get_cooperation_message(
        building_name,
        cooperation,
        cooperation_percentage,
        address,
        last_update,
        needs_update,
    )


def getUpdatedBuildingInformation(building_id):

    building_data = get_building_data(building_id=building_id)

    if not building_data:
        return "We're having trouble retrieving the building details right now. Please try again later."

    building_name = building_data.get("name")
    address = building_data.get("address")
    last_update = format_date(building_data["updated_at"])

    cooperation_info = building_data.get("cooperation", [{}])[0]
    cooperation = cooperation_info.get("cooperate")
    cooperation_percentage = cooperation_info.get("cooperation_percentage")

    if cooperation:
        cooperation_text = (
            f"cooperates at {cooperation_percentage}%"
            if cooperation_percentage
            else "cooperates"
        )
        update_message = (
            " We'll get back to you with the cooperation percentage soon. "
            if not cooperation_percentage
            else update_message
        )
        return f"Hey, you recently requested information on the {building_name}. Here's the updated information: It {cooperation_text}. It's located at {address}, and our last update for this is {last_update}. Feel free to ask us anything else!"
    else:
        return f"Hey, you recently requested information on the {building_name}. This building does not cooperate with locators at the moment. We checked this last at {last_update}. Do you have other buildings you'd like us to check?"
