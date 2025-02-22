from google.cloud import storage
import functions_framework
from PIL import Image
import json
import io
import base64

thumbnail_sizes = [(200, 200), (400, 400)]

@functions_framework.cloud_event
def generate_thumbnail(cloud_event):
    # receive cloud_event
    message = base64.b64decode(cloud_event.data["message"]["data"]).decode("utf-8")
    data = json.loads(message)
    input_bucket_name = data["input_bucket"]
    output_bucket_name = data["output_bucket"]
    file_name = data["file_name"]

    # retrieve storage data
    storage_client = storage.Client()
    input_bucket = storage_client.bucket(input_bucket_name)
    output_bucket = storage_client.bucket(output_bucket_name)
    
    # download original image
    blob = input_bucket.blob(file_name)
    image_data = blob.download_as_bytes()
    image = Image.open(io.BytesIO(image_data))
    
    # generate thumbnails of different sizes
    thumbnail_urls = {}
    for size in thumbnail_sizes:
        # create a copy of the image for this thumbnail
        thumb = image.copy()
        thumb.thumbnail(size)
        
        # save thumbnail
        thumbnail_buffer = io.BytesIO()
        thumb.save(thumbnail_buffer, format=image.format)
        thumbnail_buffer.seek(0)
        
        # generate thumbnail filename
        thumb_filename = f"thumbnails/{file_name}/{file_name.rsplit('.', 1)[0]}_{size[0]}x{size[1]}.{image.format.lower()}"
        
        # upload thumbnail
        thumbnail_blob = output_bucket.blob(thumb_filename)
        thumbnail_blob.upload_from_file(
            thumbnail_buffer,
            content_type=f'image/{image.format.lower()}'
        )
        
        thumbnail_urls[f"{size[0]}x{size[1]}"] = thumb_filename

    metadata = {}
    metadata['thumbnails'] = thumbnail_urls
    new_filename = f"thumbnails/{file_name}/metadata.json"
    new_blob = output_bucket.blob(new_filename)
    new_blob.upload_from_string(
        json.dumps(metadata),
        content_type='application/json'
    )

    return "Thumbnails generated", 200