data "archive_file" "thumbnail_generator" {
  type        = "zip"
  source_dir  = "../functions/thumbnail_generator"
  output_path = "./zipped/thumbnail_generator.zip"
}

resource "google_storage_bucket_object" "thumbnail_generator_source" {
  name   = "thumbnail_generator.zip"
  bucket = google_storage_bucket.function_source_bucket.name
  source = data.archive_file.thumbnail_generator.output_path
}

resource "google_cloudfunctions2_function" "thumbnail_generator" {
  name     = "thumbnail-generator"
  location = var.region

  build_config {
    runtime     = "python312"
    entry_point = "generate_thumbnail"
    source {
      storage_source {
        bucket = google_storage_bucket.function_source_bucket.name
        object = google_storage_bucket_object.thumbnail_generator_source.name
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
