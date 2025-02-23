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

  service_config {
    max_instance_count = local.function_config.input_handler.max_instance_count
    min_instance_count = local.function_config.input_handler.min_instance_count
    available_memory   = local.function_config.input_handler.available_memory
    timeout_seconds    = local.function_config.input_handler.timeout_seconds
  }

  depends_on = [
    google_pubsub_topic.input_bucket,
    google_project_iam_member.function_sa_roles,
    google_project_iam_member.storage_publisher,
  ]
}

resource "google_cloudfunctions2_function_iam_member" "invoker" {
  project        = google_cloudfunctions2_function.input_handler.project
  location       = google_cloudfunctions2_function.input_handler.location
  cloud_function = google_cloudfunctions2_function.input_handler.name
  role           = "roles/cloudfunctions.invoker"
  member         = "serviceAccount:${data.google_project.project.number}-compute@developer.gserviceaccount.com"
}
