import psutil
import json
import urllib.request
from tqdm import tqdm
from data_prep import format_input

def check_if_running(process_name):
    running = False
    for proc in psutil.process_iter(["name"]):
        if process_name in proc.info["name"]:
            running = True
            break
    return running


def query_model(
    prompt, 
    #model="llama3", 
    model="gemma3:1b",
    url="http://localhost:11434/api/chat"
):
    data = {             #1 Creates the data payload as a dictionary 
        "model": model,
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "options": {         #2 Settings for deterministic responses 
            "seed": 123,
            "temperature": 0,
            "num_ctx": 2048
        }
    }

    payload = json.dumps(data).encode("utf-8")    #3 Converts the dictionary to a JSON-formatted string and encodes it to bytes 
    request = urllib.request.Request(#4 Creates a request object, setting the method to POST and adding necessary headers 
        url,                                                #4
        data=payload,                                       #4
        method="POST"                                       #4
    ) #4

    request.add_header("Content-Type", "application/json")   #4

    response_data = ""
    with urllib.request.urlopen(request) as response:   #5 Sends the request and captures the response 
        while True:
            line = response.readline().decode("utf-8")
            if not line:
                break
            response_json = json.loads(line)
            response_data += response_json["message"]["content"]

    return response_data


def generate_model_scores(json_data, json_key, model="gemma3:1b"):
    scores = []
    for entry in tqdm(json_data, desc="Scoring entries"):
        prompt = (
            f"Given the input `{format_input(entry)}` "
            f"and correct output `{entry['output']}`, "
            f"score the model response `{entry[json_key]}`"
            f" on a scale from 0 to 100, where 100 is the best score. "
            f"Respond with the integer number only."   #1 Modified instruction line to only return the score
        )
        score = query_model(prompt, model)
        try:
            scores.append(int(score))
        except ValueError:
            print(f"Could not convert score: {score}")
            continue

    return scores