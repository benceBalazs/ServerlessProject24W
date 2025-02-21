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
resource "google_storage_bucket" "input_bucket" {
  name = "${var.project_id}-input"
  location = var.region
  uniform_bucket_level_access = true
}

// Set up output storage buckets
resource "google_storage_bucket" "output_bucket" {
  name = "${var.project_id}-output"
  location = var.region
  uniform_bucket_level_access = true
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

# Cloud Functions
resource "google_cloudfunctions2_function" "input_handler" {
  name = "input-handler"
  location = var.region

  build_config {
    runtime = "python311"
    entry_point = "handle_upload"
    source {
      storage_source {
        bucket = google_storage_bucket.source_bucket.name
        object = google_storage_bucket_object.input_handler_source.name
      }
    }
  }

  service_config {
    max_instance_count = 100
    available_memory   = "256M"
    timeout_seconds    = 60
  }

  event_trigger {
    trigger_region = var.region
    event_type = "google.cloud.storage.object.v1.finalized"
    event_filters = [{
      attribute = "bucket"
      value = google_storage_bucket.input_bucket.name
    }]
  }
}

resource "google_cloudfunctions2_function" "exif_processor" {
  name = "exif-processor"
  location = var.region

  build_config {
    runtime = "python311"
    entry_point = "process_exif"
    source {
      storage_source {
        bucket = google_storage_bucket.source_bucket.name
        object = google_storage_bucket_object.input_handler_source.name
      }
    }
  }

  service_config {
    max_instance_count = 100
    available_memory   = "256M"
    timeout_seconds    = 60
  }

  event_trigger {
    trigger_region = var.region
    event_type = "google.cloud.storage.object.v1.finalized"
    event_filters = [{
      attribute = "bucket"
      value = google_storage_bucket.input_bucket.name
    }]
  }
}

