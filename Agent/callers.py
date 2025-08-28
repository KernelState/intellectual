import sys
import lib
from enum import Enum
from pydantic import BaseModel
from ddgs import DDGS
from bs4 import BeautifulSoup
import requests
import logging_

prompt = "how much is 18*90"
max_chars = 500
model_name = "mistral:7b-instruct"
### During testing I found out that meta's fine tuning is more of a logical one so I had to choose this one sense mistral is mainly a verbal recognition system which is great for its use, but terrible for somethinig like choices or offline questions
offline = "llama3"

def QQA() -> str:
    return lib.call_model(offline, prompt)

QQA_tl = lib.Tool("reasoning and mathematical questions", QQA, "Answers non-informational questions", "QQA")

def look_up(prompt, times):
    res = DDGS().text(prompt, safesearch = "On", timelimit="1y", max_results=times)
    return res

def web_search() -> str:
    times = 1
    while True:
        l = logging_.Logger("WEB_AGENT")
        pages = look_up(prompt, times)
        l.info(f"[DDG_API OUTPUT] {pages}")
        results = ""
        for page in pages:
            html = requests.get(page['href'])
            soup = BeautifulSoup(html.text, 'html')
            for tag in soup(["script", "style", "header", "footer", "nav", "aside", "button", "input"]):
                tag.decompose()
            results += soup.get_text(separator=" ", strip=True) + "\n"
        if len(results) > 200 * times:
            break
    l.info(f"[TXT] {results[:1000]}") # Just to make sure DDG isnt the issue
    base = 0
    base_end = base + max_chars
    if base_end - base > max_chars:
        base_end = base + max_chars
    l.info("selecting from web data")
    i = 0
    for word in results.split(" "):
        i += len(word) + 1
        if word in prompt:
            break
    l.info(f"using a margin over index {i}")
    if len(results) < max_chars:
        base = 0
        base_end = len(results) - 1
    elif i < 500:
        base = 0
        base_end = base + max_chars
    else:
        base = i - (max_chars/2)
        base_end = base + max_chars
    results = results[base:base_end]
    pro = f"summarise only this piece of text following this topic: {prompt}, text: {results}"
    l.info(f"[PROMPT] {len(pro)} [NON] {base_end - base} [START] {base} [END] {base_end}")
    obs = lib.call_model(model_name, f"summarise this piece of text following as concisely as possible with this topic: {prompt}, text: {results}")
    l.info(f"AI summariser: {obs}")
    return obs

web_search_tl = lib.Tool("definitions and history", web_search, "Searches the web and concludes answers", "web_search_tl")

class ToolSet(str, Enum):
    QQA=QQA_tl.name
    web_search=web_search_tl.name

class Model(BaseModel):
    result: ToolSet

if "--test" in sys.argv or "-t" in sys.argv:
    tools = [QQA_tl, web_search_tl]
    a = lib.Agent("test_model", offline, [QQA_tl, web_search_tl], Model)
    print(a.pick(prompt))
