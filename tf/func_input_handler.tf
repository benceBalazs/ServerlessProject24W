data "archive_file" "input_handler" {
  type        = "zip"
  source_dir  = "../functions/input_handler"
  output_path = "./zipped/input_handler.zip"
}

resource "google_storage_bucket_object" "input_handler_source" {
  name   = "input_handler.zip"
  bucket = google_storage_bucket.function_source_bucket.name
  source = data.archive_file.input_handler.output_path
}

resource "google_cloudfunctions2_function" "input_handler" {
  name     = "input-handler"
  location = var.region

  build_config {
    runtime     = "python312"
    entry_point = "handle_upload"
    source {
      storage_source {
        bucket = google_storage_bucket.function_source_bucket.name
        object = google_storage_bucket_object.input_handler_source.name
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

  depends_on = [
    google_project_iam_member.gcs_pubsub_publisher,
    google_storage_bucket_object.input_handler_source,
    google_storage_bucket.input_bucket
  ]
}
