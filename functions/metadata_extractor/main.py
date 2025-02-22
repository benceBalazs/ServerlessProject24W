from google.cloud import storage, pubsub_v1
import functions_framework
from PIL import Image
import json
import io
import base64

project_id = "serverless-project-24W"
topics = {
    "thumbnail": f"projects/{project_id}/topics/generate-thumbnail",
    "format": f"projects/{project_id}/topics/convert-format",
    "rgb": f"projects/{project_id}/topics/separate-rgb-channels",
    "exif": f"projects/{project_id}/topics/process-exif"
}

@functions_framework.cloud_event
def extract_metadata(cloud_event):
    # receive cloud_event
    message = base64.b64decode(cloud_event.data["message"]["data"]).decode("utf-8")
    data = json.loads(message)
    input_bucket_name = data["input_bucket"]
    output_bucket_name = data["output_bucket"]
    file_name = data["file_name"]

    # retrieve storage and file data
    storage_client = storage.Client()
    input_bucket = storage_client.bucket(input_bucket_name)
    output_bucket = storage_client.bucket(output_bucket_name)
    blob = input_bucket.blob(file_name)
    
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
        "timestamp": cloud_event.get_attributes()["time"],
    }
    
    # store metadata
    metadata_blob = output_bucket.blob(f"metadata/{file_name}.json")
    metadata_blob.upload_from_string(
        json.dumps(metadata),
        content_type='application/json'
    )

    # invoke EXIF processing
    publisher = pubsub_v1.PublisherClient()
    # write to json
    message_data = json.dumps({
        "input_bucket": input_bucket_name,
        "output_bucket": output_bucket_name,
        "file_name": file_name
    }).encode("utf-8")

    # publish events
    for topic_path in topics.values():
        publisher.publish(topic_path, message_data)

    return "Metadata extracted", 200