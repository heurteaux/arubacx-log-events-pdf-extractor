import json
from openai import OpenAI
from .constants import PARSE_CACHE_FILENAME

def batch_to_json(batch_id: str, client: OpenAI, dest: str):
    batch_job = client.batches.retrieve(batch_id)
    
    result_file_id = batch_job.output_file_id
    
    file_content = client.files.content(result_file_id).content.decode("utf-8")
    
    with open(PARSE_CACHE_FILENAME, "r") as cache_r:
        cache = json.load(cache_r)

        for line in file_content.splitlines():
            json_obj = json.loads(line)
            original_id = json_obj["custom_id"].replace("-MSG", "").replace("-DESC", "").replace("-1", "")

            if original_id not in cache:
                cache[original_id] = {}
            if "-MSG" in json_obj["custom_id"]:
                cache[original_id]["message"] = json_obj["response"]["body"]["choices"][0]["message"]["content"]
            if "-DESC" in json_obj["custom_id"]:
                cache[original_id]["description"] = json_obj["response"]["body"]["choices"][0]["message"]["content"]

        with open(dest, 'w') as outfile:
            json.dump(cache, outfile, indent=4)