import os
import pandas as pd
import warnings
from dotenv import load_dotenv

from langchain.chains import LLMChain
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain_community.document_loaders import WebBaseLoader
from langchain_community.utilities import GoogleSerperAPIWrapper

warnings.filterwarnings('ignore')

# Load .env file if present
load_dotenv()

# Safely read API keys
openai_api_key = os.getenv("OPENAI_API_KEY")
serper_api_key = os.getenv("SERPER_API_KEY")

if not openai_api_key or not serper_api_key:
    raise RuntimeError(
        "Missing API keys. Please set OPENAI_API_KEY and SERPER_API_KEY in your environment or .env file."
    )


# Load fallacies dataset
csv_path = os.path.join(os.path.dirname(__file__), '..', 'fallacies.csv')
fallacies_df = pd.read_csv(csv_path)

# Define the LLM
llm = ChatOpenAI(
    temperature=0,
    model='gpt-4.1-mini',
    max_tokens=16000,
    openai_api_key=openai_api_key
)

# Prompt templates
template1 = """You are a communications expert. Given this news article, summarize it in five very clear sentences and be accurate. Do not make things up. Do not include line numbers. Check to make sure you are correct. Think step by step.

Fallacies to check:
{fallacies_df}

Article: {content}

Communications expert summary:"""

chain1 = LLMChain(
    llm=llm,
    prompt=PromptTemplate(
        input_variables=["content", "fallacies_df"],
        template=template1
    )
)

template2 = """You are an ethics professor analyzing this article summary, review using the fallacy definitions again. Be succinct and easy to read, but intelligently draw upon all ethics rules. Provide: 
1. The two most impactful fallacies found out of fallacies in the summary. 
2. Why the fallacies might mislead readers.
3. One possible alternative interpretation of why each of the fallacies could have been included, as a counterfactual and counterpoint to finding the respective key fallacy.

Do not include line numbers. Talk about each fallacy in individual paragraphs. If you cannot find more than one relevant fallacy, talk about only one.
If you cannot find any, leave blank.

Article Summary: {summary}
Fallacies to consider: 
{fallacies_df}

Professor:"""

chain2 = LLMChain(
    llm=llm,
    prompt=PromptTemplate(
        input_variables=["summary", "fallacies_df"],
        template=template2
    )
)

# News search
google_serper = GoogleSerperAPIWrapper(
    type="news",
    tbs="qdr:m1",
    serper_api_key=serper_api_key
)

# The callable agent function
def agent(query: str):
    """
    Given a topic string, searches for a relevant article,
    summarizes it, and analyzes fallacies.
    Returns a dict with title, url, summary, and analysis.
    """
    # Search whitehouse.gov news
    search_results = google_serper.results(query)

    if not search_results["news"]:
        return {"error": "No articles found."}

    article_url = search_results['news'][0]['link']
    article_title = search_results['news'][0]['title']

    # Load first article
    loader = WebBaseLoader(article_url)
    article_text = ' '.join(loader.load()[0].page_content[:3000].split())

    # Run chains
    summary = chain1.run(content=article_text, fallacies_df=fallacies_df)
    analysis = chain2.run(summary=summary, fallacies_df=fallacies_df)

    return {
        "sources": article_title + " - " + article_url,
        "summary": summary,
        "analysis": analysis,
    }
