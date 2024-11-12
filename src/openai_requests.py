from openai import OpenAI
import tempfile
import json
import time
from halo import Halo
from alive_progress import alive_bar
from .constants import *

class ProgressInfo:
    def __init__(self, batch_id: str, client: OpenAI):
        self.processed = 0
        self.batch_id = batch_id
        self.client = client
        self.batch = client.batches.retrieve(batch_id)
    
    def init_total(self):
        self.total = self.client.batches.retrieve(self.batch_id).request_counts.total

def display_spinner_result(progress: ProgressInfo, spinner: Halo):
    match progress.batch.status:
        case "cancelled":
            spinner.fail(FORMAT_FAIL("Cancelled"))
        case "failed":
            spinner.fail(FORMAT_FAIL("Failed"))
        case "expired":
            spinner.fail(FORMAT_FAIL("Expired"))
        case "in_progress":
            spinner.succeed()
        case "completed":
            spinner.succeed(FORMAT_OK("Completed"))

def check_finalization(progress: ProgressInfo):
    with Halo(text='Finalizing...') as spinner:
        while progress.batch.status == "finalizing":
            time.sleep(API_PROGRESS_REFRESH_INTERVAL)
            progress.batch = progress.client.batches.retrieve(progress.batch_id)

        if progress.batch.status == "cancelling":
            spinner.text = FORMAT_WARNING("Cancelling...")
            while progress.batch.status == "cancelling":
                time.sleep(API_PROGRESS_REFRESH_INTERVAL)
                progress.batch = progress.client.batches.retrieve(progress.batch_id)
        
        display_spinner_result(progress, spinner)
        
def check_progress(progress: ProgressInfo):
    progress.init_total()
    with alive_bar(manual=True, stats=False) as bar:
        while progress.batch.status == "in_progress":
            time.sleep(API_PROGRESS_REFRESH_INTERVAL)
            progress.processed = progress.batch.request_counts.completed
            progress.batch = progress.client.batches.retrieve(progress.batch_id)
            if progress.processed != 0 and progress.total != 0:
                bar(progress.processed / progress.total)
        if progress.batch.status == "finalizing" or progress.batch.status == "completed":
            bar(1)

def check_validation(progress: ProgressInfo):
    with Halo(text='Validating...') as spinner:
        while progress.batch.status == "validating":
            time.sleep(API_PROGRESS_REFRESH_INTERVAL)
            progress.batch = progress.client.batches.retrieve(progress.batch_id)

        if progress.batch.status == "cancelling":
            spinner.text = FORMAT_WARNING("Cancelling...")
            while progress.batch.status == "cancelling":
                time.sleep(API_PROGRESS_REFRESH_INTERVAL)
                progress.batch = progress.client.batches.retrieve(progress.batch_id)

        display_spinner_result(progress, spinner)

def display_progress(client: OpenAI, batch_id: str):
    progress = ProgressInfo(batch_id, client)
    print(INFORMATION_MESSAGE)
    check_validation(progress)
    check_progress(progress)
    check_finalization(progress)    

def save_state_ongoing_session(batch_id: str):
    json_data = {
        "batch_id": batch_id
    }

    with open(SESSION_SAVE_FILENAME, 'w') as f:
        json.dump(json_data, f)
        
def create_batch(batch_list: list, client: OpenAI) -> str:
    spinner = Halo(FORMAT_OK("Creating sanitization request to OpenAI..."))
    spinner.start()

    with tempfile.NamedTemporaryFile(mode='w+') as temp:
        for entry in batch_list:
            json.dump(entry, temp)
            temp.write('\n')

        temp.flush()
        temp.seek(0)

        with open(temp.name, "rb") as temp_r:
            batch_file = client.files.create(
                file=temp_r,
                purpose="batch"
            )

        batch_job = client.batches.create(
            input_file_id=batch_file.id,
            endpoint="/v1/chat/completions",
            completion_window="24h"
        )

    spinner.succeed()
    spinner.stop()
    
    save_state_ongoing_session(batch_job.id)

    return batch_job.id