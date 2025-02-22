from google.cloud import storage
import functions_framework
from PIL import Image
import numpy as np
import json
import io
import base64

@functions_framework.cloud_event
def separate_rgb_channels(cloud_event):
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
    blob = input_bucket.blob(file_name)
    
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
        channel_filename = f"channels/{file_name}/{file_name.rsplit('.', 1)[0]}_{channel_name}.png"
        
        # save to memory
        output_buffer = io.BytesIO()
        channel_image.save(output_buffer, format='PNG')
        output_buffer.seek(0)
        
        # upload to bucket
        channel_blob = output_bucket.blob(channel_filename)
        channel_blob.upload_from_file(
            output_buffer,
            content_type='image/png'
        )
        
        channel_urls[channel_name] = channel_filename


    metadata = {}
    metadata['rgb_channels'] = channel_urls
    new_filename = f"channels/{file_name}/metadata.json"
    new_blob = output_bucket.blob(new_filename)
    new_blob.upload_from_string(
        json.dumps(metadata),
        content_type='application/json'
    )

    return "RGB channels separated", 200