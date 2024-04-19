### Router
from typing import Literal

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_cohere import ChatCohere

### Build Index

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import WebBaseLoader
from langchain_community.vectorstores import Chroma
from langchain_cohere import CohereEmbeddings


# def getRetriever():
#     # Set embeddings
#     embd = CohereEmbeddings()

#     # Docs to index
#     urls = [
#         "https://lilianweng.github.io/posts/2023-06-23-agent/",
#         "https://lilianweng.github.io/posts/2023-03-15-prompt-engineering/",
#         "https://lilianweng.github.io/posts/2023-10-25-adv-attack-llm/",
#     ]

#     # Load
#     docs = [WebBaseLoader(url).load() for url in urls]
#     docs_list = [item for sublist in docs for item in sublist]

#     # Split
#     text_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
#         chunk_size=512, chunk_overlap=0
#     )
#     doc_splits = text_splitter.split_documents(docs_list)

#     # Add to vectorstore
#     vectorstore = Chroma.from_documents(
#         documents=doc_splits,
#         embedding=embd,
#     )

#     retriever = vectorstore.as_retriever()
#     return retriever


# # Data model
# class webSearch(BaseModel):
#     """
#     The internet. Use webSearch for questions that are related to anything else than agents, prompt engineering, and adversarial attacks.
#     """

#     query: str = Field(description="The query to use when searching the internet.")


# class vectorStore(BaseModel):
#     """
#     A vectorStore containing documents related to agents, prompt engineering, and adversarial attacks. Use the vectorStore for questions on these topics.
#     """

#     query: str = Field(description="The query to use when searching the vectorStore.")


# def routeQuestion(question: str, tool: Literal["webSearch", "vectorStore"]) -> str:
#     # Preamble
#     preamble = """You are an expert at routing a user question to a vectorStore or web search.
#     The vectorStore contains documents related to agents, prompt engineering, and adversarial attacks.
#     Use the vectorStore for questions on these topics. Otherwise, use web-search."""

#     # LLM with tool use and preamble
#     llm = ChatCohere(model="command-r", temperature=0)
#     structured_llm_router = llm.bind_tools(
#         tools=[webSearch, vectorStore], preamble=preamble
#     )

#     # Prompt
#     route_prompt = ChatPromptTemplate.from_messages(
#         [
#             ("human", "{question}"),
#         ]
#     )

#     question_router = route_prompt | structured_llm_router
#     response = question_router.invoke({"question": question})
#     print(response.response_metadata["tool_calls"])


# ### Retrieval Grader
# # Data model
# class GradeDocuments(BaseModel):
#     """Binary score for relevance check on retrieved documents."""

#     binary_score: str = Field(
#         description="Documents are relevant to the question, 'yes' or 'no'"
#     )


# def gradeRetrievedDocument(document: str, question: str) -> str:
#     # Prompt
#     preamble = """You are a grader assessing relevance of a retrieved document to a user question. \n
#     If the document contains keyword(s) or semantic meaning related to the user question, grade it as relevant. \n
#     Give a binary score 'yes' or 'no' score to indicate whether the document is relevant to the question."""

#     # LLM with function call
#     llm = ChatCohere(model="command-r", temperature=0)
#     structured_llm_grader = llm.with_structured_output(
#         GradeDocuments, preamble=preamble
#     )

#     grade_prompt = ChatPromptTemplate.from_messages(
#         [
#             (
#                 "human",
#                 "Retrieved document: \n\n {document} \n\n User question: {question}",
#             ),
#         ]
#     )

#     retriever = getRetriever()
#     retrieval_grader = grade_prompt | structured_llm_grader
#     question = "types of agent memory"
#     docs = retriever.invoke(question)
#     doc_txt = docs[1].page_content
#     response = retrieval_grader.invoke({"question": question, "document": doc_txt})
#     print(response)


