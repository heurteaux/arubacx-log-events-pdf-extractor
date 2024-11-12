import os
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))

class bcolors:
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

# Config
OPENAI_SANITIZE_MODEL = "gpt-4o-mini"
API_PROGRESS_REFRESH_INTERVAL = 5
DEBUG_NB_BATCH_ENTRIES = 5

# Text formatting
CLEAN_STR = lambda text: text.strip().replace('\n', '')
PRINT_ERR = lambda msg: print(msg, sys.stderr)
FORMAT_FAIL = lambda text: bcolors.FAIL + bcolors.BOLD + text + bcolors.ENDC
FORMAT_OK = lambda text: bcolors.OKGREEN + bcolors.BOLD + text + bcolors.ENDC
FORMAT_OKBLUE = lambda text: bcolors.OKBLUE + bcolors.BOLD + text + bcolors.ENDC
FORMAT_WARNING = lambda text: bcolors.WARNING + bcolors.BOLD + text + bcolors.ENDC

# Strings
RESUME_SESSION_PROMPT = lambda : input("An ongoing session has been detected, do you want to resume where you left ? (Y/N) : ").capitalize()
INFORMATION_MESSAGE = FORMAT_OKBLUE("\u2139\uFE0F  - OpenAI requests are made using a cost optimized service, thus requests can take up to several hours to complete.\n")

# Regex Patterns
REGEX_PATTERN = r"EventID:(?P<eventid>\d+)(?:\(Severity:\s+)?(?P<severity>[A-Za-z]+)?\)?[\s\S]*?(?:LogMessage)?[\s\S]*?(?<!Log)Message(?P<message>[\s\S]*?(?=Category|AOS-CX))[\s\S]*?Category(?P<category>[\s\S]*?(?=Severity|AOS-CX))[\s\S]*?Severity(?P<level>[\s\S]*?(?=Description|AOS-CX))[\s\S]*?Description(?P<description>.+)"

# File paths
PROMPT_LOCATION = os.path.join(current_dir, "prompts", "sanitize_log_events.txt")
SESSION_SAVE_FILENAME = ".ongoing_session.json"
PARSE_CACHE_FILENAME = ".parse_cache.tmp"
PARSE_CACHE_FILENAME = ".parse_cache.tmp"