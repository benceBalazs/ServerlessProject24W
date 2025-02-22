data "archive_file" "exif_processor" {
  type        = "zip"
  source_dir  = "../functions/exif_processor"
  output_path = "./zipped/exif_processor.zip"
}

resource "google_storage_bucket_object" "exif_processor_source" {
  name   = "exif_processor.zip"
  bucket = google_storage_bucket.function_source_bucket.name
  source = data.archive_file.exif_processor.output_path
}

resource "google_cloudfunctions2_function" "exif_processor" {
  name     = "exif-processor"
  location = var.region

  build_config {
    runtime     = "python312"
    entry_point = "process_exif"
    source {
      storage_source {
        bucket = google_storage_bucket.function_source_bucket.name
        object = google_storage_bucket_object.exif_processor_source.name
      }
    }
  }

  event_trigger {
    trigger_region = var.region
    event_type     = "google.cloud.pubsub.topic.v1.messagePublished"
    pubsub_topic   = google_pubsub_topic.process_exif.id
    retry_policy   = "RETRY_POLICY_RETRY"
  }

  depends_on = [
    google_project_iam_member.gcs_pubsub_publisher,
    google_storage_bucket_object.exif_processor_source,
    google_pubsub_topic.process_exif
  ]
}
