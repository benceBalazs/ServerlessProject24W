data "archive_file" "rgb_channel_separator" {
  type        = "zip"
  source_dir  = "../functions/rgb_channel_separator"
  output_path = "./zipped/rgb_channel_separator.zip"
}

resource "google_storage_bucket_object" "rgb_channel_separator_source" {
  name   = "rgb_channel_separator.zip"
  bucket = google_storage_bucket.function_source_bucket.name
  source = data.archive_file.rgb_channel_separator.output_path
}

resource "google_cloudfunctions2_function" "rgb_channel_separator" {
  name     = "rgb-channel-separator"
  location = var.region

  build_config {
    runtime     = "python311"
    entry_point = "separate_rgb_channels"
    source {
      storage_source {
        bucket = google_storage_bucket.function_source_bucket.name
        object = google_storage_bucket_object.rgb_channel_separator_source.name
      }
    }
  }

  event_trigger {
    trigger_region = var.region
    event_type     = "google.cloud.pubsub.topic.v1.messagePublished"
    pubsub_topic   = google_pubsub_topic.separate_rgb_channels.id
    retry_policy   = "RETRY_POLICY_RETRY"
  }

  depends_on = [
    google_project_iam_member.gcs_pubsub_publisher,
    google_storage_bucket_object.rgb_channel_separator_source,
    google_pubsub_topic.separate_rgb_channels
  ]
}
