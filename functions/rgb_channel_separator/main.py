from google.cloud import storage
import functions_framework
from PIL import Image
import numpy as np
import json
import io

@functions_framework.cloud_event
def separate_rgb_channels(cloud_event):
    # receive cloud_event
    data = json.loads(cloud_event.data["message"]["data"])
    bucket_name = data["bucket"]
    file_name = data["file_name"]

    # retrieve storage data
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(file_name)
    
    # download image
    image_data = blob.download_as_bytes()
    image = Image.open(io.BytesIO(image_data))
    
    # convert to RGB if not already
    if image.mode != 'RGB':
        image = image.convert('RGB')
    
    # split into channels
    r, g, b = image.split()
    
    # save each channel
    channels = {
        'red': r,
        'green': g,
        'blue': b
    }
    
    channel_urls = {}
    
    for channel_name, channel_image in channels.items():
        # create filename for this channel
        channel_filename = f"channels/{file_name.rsplit('.', 1)[0]}_{channel_name}.png"
        
        # save to memory
        output_buffer = io.BytesIO()
        channel_image.save(output_buffer, format='PNG')
        output_buffer.seek(0)
        
        # upload to bucket
        channel_blob = bucket.blob(channel_filename)
        channel_blob.upload_from_file(
            output_buffer,
            content_type='image/png'
        )
        
        channel_urls[channel_name] = channel_filename

    # update metadata with channel information
    try:
        metadata_blob = bucket.blob(f"metadata/{file_name}.json")
        if metadata_blob.exists():
            metadata = json.loads(metadata_blob.download_as_string())
            metadata['rgb_channels'] = channel_urls
            metadata_blob.upload_from_string(
                json.dumps(metadata),
                content_type='application/json'
            )
    except Exception as e:
        print(f"Error updating metadata: {str(e)}")

    return "RGB channels separated", 200