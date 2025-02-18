from google.cloud import storage, pubsub_v1
import functions_framework
import json

publisher = pubsub_v1.PublisherClient()
storage_client = storage.Client()
project_id = "serverless-project-24W"
topics = {
    "metadata": f"projects/{project_id}/topics/extract-metadata",
    "thumbnail": f"projects/{project_id}/topics/generate-thumbnail",
    "format": f"projects/{project_id}/topics/convert-format",
    "rgb": f"projects/{project_id}/topics/separate-rgb-channels"
}

@functions_framework.cloud_event
def handle_upload(cloud_event):
    data = cloud_event.data

    # file name exists 
    if "name" not in data:
        return "No file name provided", 400

    file_name = data["name"]
    bucket_name = data["bucket"]

    # file has allowed format    
    if not (file_name.lower().endswith(('.jpg', '.jpeg', '.png'))):
        return "Invalid file format", 400
    
    # write to json
    message_data = json.dumps({
        "bucket": bucket_name,
        "file_name": file_name
    }).encode("utf-8")

    # publish events
    for topic_path in topics.values():
        publisher.publish(topic_path, message_data)

    return "Processing started", 200