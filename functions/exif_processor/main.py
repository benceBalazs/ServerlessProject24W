from google.cloud import storage
import functions_framework
from PIL import Image
import PIL.ExifTags
import json
import io

@functions_framework.cloud_event
def process_exif(cloud_event):
    # receive cloud_event
    data = json.loads(cloud_event.data["message"]["data"])
    bucket_name = data["bucket"]
    file_name = data["file_name"]
    metadata_path = data["metadata_path"]

    # retrieve storage and file data
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(file_name)
    
    # download image
    image_data = blob.download_as_bytes()
    image = Image.open(io.BytesIO(image_data))
    
    # extract EXIF data
    exif_data = {}
    if hasattr(image, '_getexif') and image._getexif() is not None:
        for tag_id in image._getexif():
            try:
                tag = PIL.ExifTags.TAGS.get(tag_id, tag_id)
                data = image._getexif()[tag_id]
                # convert to string if data is not serializable
                if isinstance(data, bytes):
                    data = data.decode()
                exif_data[tag] = str(data)
            except Exception as e:
                exif_data[f"error_{tag_id}"] = str(e)

    # read existing metadata
    metadata_blob = bucket.blob(metadata_path)
    metadata = json.loads(metadata_blob.download_as_string())
    
    # update with EXIF data
    metadata['exif'] = exif_data
    
    # save updated metadata
    metadata_blob.upload_from_string(
        json.dumps(metadata),
        content_type='application/json'
    )

    return "EXIF data processed", 200