from concurrent.futures import ThreadPoolExecutor
import concurrent.futures
from huey.contrib.djhuey import task
from .models import push, batch
from django.core.files import File
from django.utils import timezone
import backoff
import datetime
import uuid
import requests
import os

@task()
def batch_file(p):
    endpoint = p.endpoint.url
    p.status = "Batching"
    p.save()
    if os.path.exists(p.json_file.url):
        with open(p.json_file.url, "r") as f:
            json_batch = []
            obj_list = []
            for line in f:
                json_batch.append(line)
                if len(json_batch) == 999:
                    obj_list.append(batch(json=json_batch, push=p))
                    json_batch = []
            if json_batch:
                obj_list.append(batch(json=json_batch, push=p))    
                json_batch = []
            batch.objects.bulk_create(obj_list, batch_size=250)
            p.status = "In Progress"
            p.save()
            with ThreadPoolExecutor(max_workers=int(p.workers)) as executor:
                results = {executor.submit(send_request, obj, endpoint, p) for obj in obj_list}
                for future in concurrent.futures.as_completed(results):
                    response = future.result()
                all_batches_completed = all(batch.completed or batch.failed for batch in p.batch_set.all())
                if all_batches_completed:
                    os.remove(p.json_file.url)
                    p.status = "Complete"
                    p.save()
                    
@backoff.on_exception(backoff.expo, (requests.exceptions.RequestException), max_tries=3)
def send_request(batch, endpoint, p):
    print("Worker: " + str(os.getpid()))
    try:
        headers = {'Content-type': 'text/plain'}
        response = requests.post(endpoint, data="".join(batch.json), headers=headers)
        if response.status_code == 200 and response.text[:3] != "500":
            status = response.status_code
            batch.completed = True
            batch.status = status
            batch.status_message = response.text
            batch.finished = datetime.datetime.now(tz=timezone.utc)
            batch.save()
        else:
            status = response.status_code
            batch.completed = True
            batch.failed = True
            batch.status = status
            batch.status_message = response.text
            batch.finished = datetime.datetime.now(tz=timezone.utc)
            batch.save()
    except Exception as e:
        batch.completed = True
        batch.failed = True
        batch.status = e
        batch.finished = datetime.datetime.now(tz=timezone.utc)
        batch.save()
        return e
    

