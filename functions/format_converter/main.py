from google.cloud import storage
import functions_framework
from PIL import Image
import json
import io
import base64

formats = ['JPEG', 'PNG', 'WEBP']

@functions_framework.cloud_event
def convert_format(cloud_event):
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

    # convert to different formats    
    converted_urls = {}
    for format_name in formats:
        if format_name.upper() != image.format:
            # convert image
            output_buffer = io.BytesIO()
            image.save(output_buffer, format=format_name)
            output_buffer.seek(0)
            
            # generate new filename
            new_filename = f"converted/{file_name.rsplit('.', 1)[0]}.{format_name.lower()}"
            new_blob = output_bucket.blob(new_filename)
            
            # upload converted image
            new_blob.upload_from_file(
                output_buffer,
                content_type=f'image/{format_name.lower()}'
            )
            
            converted_urls[format_name.lower()] = new_filename

    # update metadata with conversion information
    try:
        metadata_blob = output_bucket.blob(f"metadata/{file_name}.json")
        if metadata_blob.exists():
            metadata = json.loads(metadata_blob.download_as_string())
            metadata['converted_formats'] = converted_urls
            metadata_blob.upload_from_string(
                json.dumps(metadata),
                content_type='application/json'
            )
    except Exception as e:
        print(f"Error updating metadata: {str(e)}")

    return "Format conversion completed", 200