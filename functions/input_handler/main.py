from google.cloud import storage, pubsub_v1
import functions_framework
import json

publisher = pubsub_v1.PublisherClient()
storage_client = storage.Client()
project_id = "serverless-project-24W"
topics = {
    "metadata": f"projects/{project_id}/topics/extract-metadata"
}

@functions_framework.cloud_event
def handle_upload(cloud_event):
    data = cloud_event.data

    # file name exists 
    if "name" not in data:
        return "No file name provided", 400

    file_name = data["name"]
    input_bucket_name = data["bucket"]
    output_bucket_name = "serverless-project-24w-output"

    # file has allowed format    
    if not (file_name.lower().endswith(('.jpg', '.jpeg', '.png'))):
        return "Invalid file format", 400
    
    # write to json
    message_data = json.dumps({
        "input_bucket": input_bucket_name,
        "output_bucket": output_bucket_name,
        "file_name": file_name
    }).encode("utf-8")

    # publish events
    for topic_path in topics.values():
        publisher.publish(topic_path, message_data)

    return "Processing started", 200