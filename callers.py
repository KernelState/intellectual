
# requirements:
# pip install langchain langchain-community duckduckgo-search ollama

from langchain_community.llms import Ollama
from langchain.agents import initialize_agent, Tool, AgentType
from langchain_community.utilities import DuckDuckGoSearchAPIWrapper


# ---- Local Model (Ollama, supports CUDA, Metal, OpenCL depending on your setup) ----
llm = Ollama(model="llama3")  # you can switch to "mistral", "codellama", etc.

# ---- Web Search Tool ----
search = DuckDuckGoSearchAPIWrapper()


