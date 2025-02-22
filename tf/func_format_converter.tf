data "archive_file" "format_converter" {
  type        = "zip"
  source_dir  = "../functions/format_converter"
  output_path = "./zipped/format_converter.zip"
}

resource "google_storage_bucket_object" "format_converter_source" {
  name   = "format_converter.zip"
  bucket = google_storage_bucket.function_source_bucket.name
  source = data.archive_file.format_converter.output_path
}

resource "google_cloudfunctions2_function" "format_converter" {
  name     = "format-converter"
  location = var.region

  build_config {
    runtime     = "python312"
    entry_point = "convert_format"
    source {
      storage_source {
        bucket = google_storage_bucket.function_source_bucket.name
        object = google_storage_bucket_object.format_converter_source.name
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
