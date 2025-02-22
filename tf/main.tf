terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 4.0"
    }
  }
}

provider "google" {
  project = var.project_id
  region  = var.region
}

data "google_project" "project" {}

resource "google_project_iam_member" "function_sa_roles" {
  for_each = toset([
    "roles/storage.objectViewer",
    "roles/pubsub.editor",
    "roles/pubsub.publisher",
    "roles/eventarc.eventReceiver",
    "roles/cloudfunctions.invoker",
  ])

  project = var.project_id
  role    = each.key
  member  = "serviceAccount:${data.google_project.project.number}-compute@developer.gserviceaccount.com"
}

resource "google_project_iam_member" "storage_publisher" {
  project = var.project_id
  role    = "roles/pubsub.publisher"
  member  = "serviceAccount:service-${data.google_project.project.number}@gs-project-accounts.iam.gserviceaccount.com"
}

# resource "google_eventarc_trigger" "input_handler_trigger" {
#   name     = "input-handler-trigger"
#   location = var.region

#   matching_criteria {
#     attribute = "bucket"
#     value     = google_storage_bucket.input_bucket.name
#   }

#   matching_criteria {
#     attribute = "type"
#     value     = "google.cloud.storage.object.v1.finalized"
#   }

#   destination {
#     cloud_function = google_cloudfunctions2_function.input_handler.name
#   }

#   transport {
#     pubsub {
#       topic = google_pubsub_topic.input_bucket.name
#     }
#   }

#   depends_on = [google_project_iam_member.function_sa_roles]
# }

# Buckets

resource "google_storage_bucket" "function_source_bucket" {
  name                        = "${var.project_id}-functions"
  location                    = var.region
  uniform_bucket_level_access = true
}

resource "google_storage_bucket" "input_bucket" {
  name                        = "${var.project_id}-input"
  location                    = var.region
  uniform_bucket_level_access = true
}

resource "google_storage_bucket" "output_bucket" {
  name                        = "${var.project_id}-output"
  location                    = var.region
  uniform_bucket_level_access = true
}

# PubSub Topics

resource "google_pubsub_topic" "input_bucket" {
  name = "input-bucket"
}

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

