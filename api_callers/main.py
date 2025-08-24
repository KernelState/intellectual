import os
import io
import json
import trafilatura
from ddg import Duckduckgo
from bs4 import BeautifulSoup
import requests
import ollama
import time
import json
import sys

buffer = io.StringIO()
old_stdout = sys.stdout
sys.stdout = buffer

if len(sys.argv) < 2:
    print("too few arguments")
    quit(1)
json_path = sys.argv[1]
if not os.path.exists(json_path):
    print("file not found")
payload_config = {}
with open(json_path, "r") as file:
    payload_config = json.load(file)
print(f"payload_config: {payload_config}")
model = payload_config["model"]
website_cap = payload_config["website_cap"]
limit = payload_config["limit"]
limit_alt = payload_config["limit_alt"]
run = payload_config["run"]
run_args = payload_config["run_args"]
output = payload_config["output_json"]
web = payload_config["web"]
ddg_api = Duckduckgo()
if os.path.exists(output):
    print("[WARN] The output file already exists overwriting")

class Query:
    def __init__(self, prompt = "", system = ""):
        self.prompt = prompt
        self.system = system
        self.created = time.time_ns()
    def set_system(self, system):
        self.system = system
    def set_prompt(self, prompt):
        self.prompt = prompt
    def will_search(self) -> bool:
        if self.prompt == "":
            raise Exception("prompt is empty")
        chunk = ollama.chat(
            model=model,
            messages=
            [{"role": "system", "content": "You are a model used to check if a question is in this models ability to answer, if you can return \"True\" otherwise reutrn \"False\""}
             , {"role": "user", "content": f"can you answer this question: {self.prompt}"}],
        )
        return chunk["message"]["content"]
    def web_search(self) -> str:
        self.ran = time.time_ns()
        stream = ddg_api.search(self.prompt)
        contexts = ""
        print("loading web data")
        for i in range(website_cap):
            if len(stream["data"]) < (i+1):
                print("[WARN] not enough results, skipping")
            website = stream["data"][i]
            if len(website) > limit:
                website = website[0:limit_alt]
            downloaded = trafilatura.fetch_url(website["url"])
            text = trafilatura.extract(downloaded)
            contexts += str(text)
        print(f"contexts: {contexts}")
        print("Generating answer")
        chunk = ollama.chat(model=model,
                            messages=
                            [{"role": "system", "content": f"You are a summarizer. Only output the summary. Do not add explanations or preambles and make sure you fit these requirements: {self.system}"},
                             {"role": "user", "content": f"summarize this: {contexts}"}
                             ]
                            ) # wtf is this indentaion? idk, I hate python
        self.done = time.time_ns()
        self.duration = self.done - self.ran
        print("duration:", self.duration / 1000000000)
        return str(chunk["message"]["content"]).replace("Sure, here is the summary you requested:\n", "")
    def run(self) -> str:
        self.ran = time.time_ns()
        offline_model = payload_config["enhanced_offline"] if payload_config["enhanced_offline"] else model
        result = ollama.chat(model=offline_model,
                           messages=[{"role": "system", "content": self.system},
                           {"role": "user", "content": self.prompt}])["message"]["content"]
        self.done = time.time_ns()
        self.duration = self.done - self.ran
        return result.replace("**Summary**:", "")


if run:
    q = Query(run_args["prompt"], run_args["system"])
    result = q.run() if not web else q.web_search()
    sys.stdout = old_stdout
    print(buffer.getvalue())
    output_data = {
        "logs": buffer.getvalue(),
        "response": result,
        "duration": q.duration,
        "ran": q.ran,
        "done": q.done,
    }
    with open(output, "w") as file:
        json.dump(output_data, file)
    quit(0)
