data "archive_file" "metadata_extractor" {
  type        = "zip"
  source_dir  = "../functions/metadata_extractor"
  output_path = "./zipped/metadata_extractor.zip"
}

resource "google_storage_bucket_object" "metadata_extractor_source" {
  name   = "metadata_extractor.zip"
  bucket = google_storage_bucket.function_source_bucket.name
  source = data.archive_file.metadata_extractor.output_path
}

resource "google_cloudfunctions2_function" "metadata_extractor" {
  name     = "metadata-extractor"
  location = var.region

  build_config {
    runtime     = "python312"
    entry_point = "extract_metadata"
    source {
      storage_source {
        bucket = google_storage_bucket.function_source_bucket.name
        object = google_storage_bucket_object.metadata_extractor_source.name
      }
    }
  }

  event_trigger {
    trigger_region = var.region
    event_type     = "google.cloud.storage.object.v1.finalized"
    event_filters {
      attribute = "bucket"
      value     = google_storage_bucket.input_bucket.name
    }
  }

  depends_on = [google_project_iam_member.gcs_pubsub_publisher]
}
