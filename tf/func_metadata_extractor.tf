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
    event_type     = "google.cloud.pubsub.topic.v1.messagePublished"
    pubsub_topic   = google_pubsub_topic.extract_metadata.id
    retry_policy   = "RETRY_POLICY_RETRY"
  }

  service_config {
    max_instance_count = local.function_config.metadata_extractor.max_instance_count
    min_instance_count = local.function_config.metadata_extractor.min_instance_count
    available_memory   = local.function_config.metadata_extractor.available_memory
    timeout_seconds    = local.function_config.metadata_extractor.timeout_seconds
  }

  depends_on = [
    google_project_iam_member.function_sa_roles,
    google_storage_bucket_object.metadata_extractor_source,
    google_pubsub_topic.extract_metadata
  ]
}
