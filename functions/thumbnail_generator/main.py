from google.cloud import storage
import functions_framework
from PIL import Image
import json
import io

thumbnail_sizes = [(200, 200), (400, 400)]

@functions_framework.cloud_event
def generate_thumbnail(cloud_event):
    # receive cloud_event
    message = base64.b64decode(cloud_event.data["message"]["data"]).decode("utf-8")
    data = json.loads(message)
    bucket_name = data["bucket"]
    file_name = data["file_name"]

    # retrieve storage data
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    
    # download original image
    blob = bucket.blob(file_name)
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
        thumb_filename = f"thumbnails/{file_name.rsplit('.', 1)[0]}_{size[0]}x{size[1]}.{image.format.lower()}"
        
        # upload thumbnail
        thumbnail_blob = bucket.blob(thumb_filename)
        thumbnail_blob.upload_from_file(
            thumbnail_buffer,
            content_type=f'image/{image.format.lower()}'
        )
        
        thumbnail_urls[f"{size[0]}x{size[1]}"] = thumb_filename

    # update metadata with thumbnail information
    try:
        metadata_blob = bucket.blob(f"metadata/{file_name}.json")
        if metadata_blob.exists():
            metadata = json.loads(metadata_blob.download_as_string())
            metadata['thumbnails'] = thumbnail_urls
            metadata_blob.upload_from_string(
                json.dumps(metadata),
                content_type='application/json'
            )
    except Exception as e:
        print(f"Error updating metadata: {str(e)}")

    return "Thumbnails generated", 200