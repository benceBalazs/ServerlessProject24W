from google.cloud import storage, pubsub_v1
import functions_framework
from PIL import Image
import json
import io

project_id = "serverless-project-24W"
topic_path = f"projects/{project_id}/topics/process-exif"

@functions_framework.cloud_event
def extract_metadata(cloud_event):
    # receive cloud_event
    data = json.loads(cloud_event.data["message"]["data"])
    bucket_name = data["bucket"]
    file_name = data["file_name"]

    # retrieve storage and file data
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(file_name)
    
    # download image
    image_data = blob.download_as_bytes()
    image = Image.open(io.BytesIO(image_data))
    
    # extract basic metadata
    metadata = {
        "format": image.format,
        "size": image.size,
        "mode": image.mode,
        "width": image.width,
        "height": image.height,
        "filename": file_name,
        "timestamp": cloud_event.time,
    }
    
    # store metadata
    metadata_blob = bucket.blob(f"metadata/{file_name}.json")
    metadata_blob.upload_from_string(
        json.dumps(metadata),
        content_type='application/json'
    )

    # invoke EXIF processing
    publisher = pubsub_v1.PublisherClient()
    message_data = json.dumps({
        "bucket": bucket_name,
        "file_name": file_name,
        "metadata_path": f"metadata/{file_name}.json"
    }).encode("utf-8")
    publisher.publish(topic_path, message_data)

    return "Metadata extracted", 200