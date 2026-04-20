from langchain_tavily import TavilySearch
from dotenv import load_dotenv
import os

load_dotenv()

def search_on_internet(query):

    search = TavilySearch(tavily_api_key=os.getenv("TAVILY_API_KEY"), max_results=5)

    result = search.invoke(query)
    all_findings = result["results"]

    return all_findings
