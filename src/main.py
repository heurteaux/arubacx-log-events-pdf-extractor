import pypdf, re, sys, argparse, os, json, dotenv
from openai import OpenAI
from .constants import *
from .openai_requests import create_batch, display_progress
from .convert_batch_result import batch_to_json
from halo import Halo

class UsrRequest:
    def __init__(self):
        parser = argparse.ArgumentParser(description="Converts ArubaCX PDF log events documentation to a usable JSON file")
        parser.add_argument("src", type=str, help="Path to the source PDF file")
        parser.add_argument("dest", type=str, help="Path for the converted JSON file")
        args = parser.parse_args()

        self.src = args.src
        self.dest = args.dest
    
def remove_session_files():
    if os.path.isfile(SESSION_SAVE_FILENAME):
        os.remove(SESSION_SAVE_FILENAME)
    if os.path.isfile(PARSE_CACHE_FILENAME):
        os.remove(PARSE_CACHE_FILENAME)

def usr_session_prompt_response():
    user_choice = RESUME_SESSION_PROMPT()
    while user_choice.capitalize() not in ['Y', 'N']:
        user_choice = RESUME_SESSION_PROMPT()
    return user_choice

def space_log_prompt() -> str:
    with open(PROMPT_LOCATION, "r", encoding="utf-8") as f:
        prompt = f.read()
    return prompt

def pdf_content(filename) -> str:
    with Halo(FORMAT_OK("Reading PDF source file...")) as spinner:
        try:
            pdf_file_obj = open(filename, 'rb')
        except FileNotFoundError:
            spinner.fail()
            PRINT_ERR(FORMAT_FAIL(f"File \"{filename}\" not found"))
            exit(1)

        try:
            pdf_reader = pypdf.PdfReader(pdf_file_obj)
        except:
            spinner.fail()
            PRINT_ERR(FORMAT_FAIL("Invalid PDF file"))
            exit(1)

        try:
            pdf_text = ""

            if len(pdf_reader.pages) == 0:
                raise ValueError("Empty document")

            for page_num in range(len(pdf_reader.pages)):
                page = pdf_reader.pages[page_num]
                pdf_text += page.extract_text()
                pdf_text += "\n"
        except ValueError:
            spinner.fail()
            PRINT_ERR(FORMAT_FAIL("Empty document"))
            sys.exit(1)
        except Exception:
            spinner.fail()
            PRINT_ERR(FORMAT_FAIL("Cannot extract file content"))
            sys.exit(1)

        spinner.succeed()
    return pdf_text

def rename_on_collision(name: str, used_names: list) -> str:
    if name in used_names:
        name += "-1"
        rename_on_collision(name, used_names)
    used_names.append(name)

    return name

def create_batch_item(content: str, custom_id: str) -> dict:
    item = {}
    body = {}

    body["model"] = OPENAI_SANITIZE_MODEL
    body["messages"] = [
        {
            "role": "system",
            "content": space_log_prompt()
        },
        {
            "role": "user",
            "content": content
        }
    ]
    body["temperature"] = 0.25
    body["max_tokens"] = 1000
    body["top_p"] = 0.25

    item["body"] = body
    item["custom_id"] = custom_id
    item["method"] = "POST"
    item["url"] = "/v1/chat/completions"

    return item

def add_batch_request(match: re.Match, batch_requests: list, used_names: list):
    event_id = match.group("eventid")
    msg_name = rename_on_collision(event_id + "-MSG", used_names)
    description_name = rename_on_collision(event_id + "-DESC", used_names)
    msg_content = CLEAN_STR(match.group("message"))
    description_content = CLEAN_STR(match.group("description"))

    msg_request = create_batch_item(msg_content, msg_name)
    description_request = create_batch_item(description_content, description_name)

    batch_requests.append(msg_request)
    batch_requests.append(description_request)

def add_incomplete_object(match: re.Match, incomplete_objects: list):
    json_object = {}

    event_id = match.group("eventid")

    if match.group("severity") is None:
        json_object["severity"] = None
    else:
        json_object["severity"] = CLEAN_STR(match.group("severity"))
    
    json_object["category"] = CLEAN_STR(match.group("category"))
    json_object["level"] = CLEAN_STR(match.group("level"))
    json_object["event_id"] = int(event_id)
    
    incomplete_objects[event_id] = json_object

def parse_src_file(src_file_content: list) -> list:
    with Halo(FORMAT_OK("Parsing...")) as spinner:
        matches = re.finditer(REGEX_PATTERN, src_file_content)
        batch_requests = []
        used_names = []
        incomplete_objects = {}

        for match in matches:
            add_batch_request(match, batch_requests, used_names)
            add_incomplete_object(match, incomplete_objects)

        if len(batch_requests) == 0:
            spinner.fail()
            print(FORMAT_FAIL("Cannot find logs in PDF source file"))
            sys.exit(1)
        spinner.succeed()

        with open(PARSE_CACHE_FILENAME, "w") as cache:
            json.dump(incomplete_objects, cache)

    return batch_requests

def resume_session():
    client = OpenAI()
    usr_request = UsrRequest()
    batch_id = ""

    with open(SESSION_SAVE_FILENAME, "r") as session:
        batch_id = json.load(session)["batch_id"]

    display_progress(client, batch_id)
    batch_to_json(batch_id, client, usr_request.dest)
    remove_session_files()
    sys.exit(0)

def new_session():
    client = OpenAI()

    usr_request = UsrRequest()
    pdf_text = pdf_content(usr_request.src)
    batch_file = parse_src_file(pdf_text)
    batch_id = create_batch(batch_file, client)
    display_progress(client, batch_id)
    batch_to_json(batch_id, client, usr_request.dest)
    remove_session_files()

def main():
    if os.path.isfile(SESSION_SAVE_FILENAME):
        if usr_session_prompt_response() == 'Y':
            resume_session()
        else:
            remove_session_files()

    new_session()

if __name__ == "__main__":
    dotenv.load_dotenv()
    main()
