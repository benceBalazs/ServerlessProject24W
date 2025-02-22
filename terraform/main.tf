// set up tf & cloud provider
terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 4.0"
    }
  }
}

// Set up cloud provider environment
provider "google" {
  project = var.project_id
  region = var.region
}

// Set up input storage buckets
data "google_storage_bucket" "input_bucket" {
  name = "${var.project_id}-input"
}

// Set up output storage buckets
data "google_storage_bucket" "output_bucket" {
  name = "${var.project_id}-output"
}


// set up pub/sub topics for functions communication
resource "google_pubsub_topic" "extract_metadata" {
  name = "extract-metadata"
}

resource "google_pubsub_topic" "process_exif" {
  name = "process-exif"
}

resource "google_pubsub_topic" "generate_thumbnail" {
  name = "generate-thumbnail"
}

resource "google_pubsub_topic" "convert_format" {
  name = "convert-format"
}

resource "google_pubsub_topic" "separate_rgb_channels" {
  name = "separate-rgb-channels"
}

# CLOUD FUNCTIONS
resource "google_cloudfunctions2_function" "input_handler" {
  name = "input-handler"
  location = var.region

  build_config {
    runtime = "python311"
    entry_point = "handle_upload"
    source {
      storage_source {
        bucket = data.google_storage_bucket.input_bucket.name  
        object = google_storage_bucket_object.input_handler_source.name
      }
    }
  }
  service_config {
    max_instance_count = 100
    available_memory   = var.function_memory["input_handler"]
    timeout_seconds    = var.function_timeout["input_handler"]
  }
  event_trigger {
    trigger_region = var.region
    event_type = "google.cloud.storage.object.v1.finalized"
    event_filters {
      attribute = "bucket"
      value = data.google_storage_bucket.input_bucket.name
    }
  }
}
resource "google_storage_bucket_object" "input_handler_source" {
  name   = "input_handler.zip"  
  bucket = data.google_storage_bucket.input_bucket.name
  source = "G:/Desktop/ServerlessProject24W-main/functions/input_handler.zip"  
}

# EXIF processor
resource "google_cloudfunctions2_function" "exif_processor" {
  name = "exif-processor"
  location = var.region

  build_config {
    runtime = "python311"
    entry_point = "process_exif"
    source {
      storage_source {
        bucket = data.google_storage_bucket.input_bucket.name
        object = google_storage_bucket_object.exif_processor_source.name
      }
    }
  }
  service_config {
    max_instance_count = 100
    available_memory   = var.function_memory["exif_processor"]
    timeout_seconds    = var.function_timeout["exif_processor"]
  }
  event_trigger {
    trigger_region = var.region
    event_type = "google.cloud.storage.object.v1.finalized"
    event_filters {
      attribute = "bucket"
      value = data.google_storage_bucket.input_bucket.name
    }
  }
}
resource "google_storage_bucket_object" "exif_processor_source" {
  name   = "exif_processor.zip"  
  bucket = data.google_storage_bucket.input_bucket.name
  source = "G:/Desktop/ServerlessProject24W-main/functions/exif_processor.zip" 
}

#Format conversion 
resource "google_cloudfunctions2_function" "format_converter" {
  name = "format-converter"
  location = var.region

  build_config {
    runtime = "python311"
    entry_point = "convert_format"
    source {
      storage_source {
        bucket = data.google_storage_bucket.input_bucket.name
        object = google_storage_bucket_object.format_converter_source.name
      }
    }
  }
  service_config {
    max_instance_count = 100
    available_memory   = var.function_memory["format_converter"]
    timeout_seconds    = var.function_timeout["format_converter"]
  }
  event_trigger {
    trigger_region = var.region
    event_type = "google.cloud.storage.object.v1.finalized"
    event_filters {
      attribute = "bucket"
      value = data.google_storage_bucket.input_bucket.name
    }
  }
}
resource "google_storage_bucket_object" "format_converter_source" {
  name   = "exif_processor.zip"  
  bucket = data.google_storage_bucket.input_bucket.name
  source = "G:/Desktop/ServerlessProject24W-main/functions/format_converter.zip" 
}

#Metadata extractor
resource "google_cloudfunctions2_function" "metadata_extractor" {
  name     = "metadata-extractor"
  location = var.region

  build_config {
    runtime     = "python311"
    entry_point = "extract_metadata"
    source {
      storage_source {
        bucket = data.google_storage_bucket.input_bucket.name
        object = google_storage_bucket_object.metadata_extractor_source.name
      }
    }
  }

  service_config {
    max_instance_count = 100
    available_memory   = var.function_memory["metadata_extractor"]
    timeout_seconds    = var.function_timeout["metadata_extractor"]
  }

  event_trigger {
    trigger_region = var.region
    event_type     = "google.cloud.pubsub.topic.v1.messagePublished"
    event_filters {
      attribute = "topic"
      value     = google_pubsub_topic.extract_metadata.name
    }
  }

  depends_on = [google_pubsub_topic.extract_metadata]
}
resource "google_storage_bucket_object" "metadata_extractor_source" {
  name   = "metadata_extractor.zip"  
  bucket = data.google_storage_bucket.input_bucket.name
  source = "G:/Desktop/ServerlessProject24W-main/functions/metadata_extractor.zip" 
}

#Thumbnail Generation
resource "google_cloudfunctions2_function" "thumbnail_generator" {
  name     = "thumbnail-generator"
  location = var.region

  build_config {
    runtime     = "python311"
    entry_point = "generate_thumbnail"
    source {
      storage_source {
        bucket = data.google_storage_bucket.input_bucket.name
        object = google_storage_bucket_object.thumbnail_generator_source.name
      }
    }
  }

  service_config {
    max_instance_count = 100
    available_memory   = var.function_memory["thumbnail_generator"]
    timeout_seconds    = var.function_timeout["thumbnail_generator"]
  }

  event_trigger {
    trigger_region = var.region
    event_type     = "google.cloud.pubsub.topic.v1.messagePublished"
    event_filters {
      attribute = "topic"
      value     = google_pubsub_topic.generate_thumbnail.name
    }
  }

  depends_on = [google_pubsub_topic.generate_thumbnail]
}
resource "google_storage_bucket_object" "thumbnail_generator_source" {
  name   = "thumbnail_generator.zip"  
  bucket = data.google_storage_bucket.input_bucket.name
  source = "G:/Desktop/ServerlessProject24W-main/functions/thumbnail_generator.zip" 
}

#RGB channel separator
resource "google_cloudfunctions2_function" "rgb_channel_separator" {
  name     = "rgb-channel-separator"
  location = var.region

  build_config {
    runtime     = "python311"
    entry_point = "separate_rgb_channels"
    source {
      storage_source {
        bucket = data.google_storage_bucket.input_bucket.name
        object = google_storage_bucket_object.rgb_channel_separator_source.name
      }
    }
  }

  service_config {
    max_instance_count = 100
    available_memory   = var.function_memory["rgb_channel_separator"]
    timeout_seconds    = var.function_timeout["rgb_channel_separator"]
  }

  event_trigger {
    trigger_region = var.region
    event_type     = "google.cloud.pubsub.topic.v1.messagePublished"
    event_filters {
      attribute = "topic"
      value     = google_pubsub_topic.separate_rgb_channels.name
    }
  }

  depends_on = [google_pubsub_topic.separate_rgb_channels]
}
resource "google_storage_bucket_object" "rgb_channel_separator_source" {
  name   = "rgb_channel_separator.zip"  
  bucket = data.google_storage_bucket.input_bucket.name
  source = "G:/Desktop/ServerlessProject24W-main/functions/rgb_channel_separator.zip" 
}