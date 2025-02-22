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

resource "google_project_iam_member" "gcs_pubsub_publisher" {
  project = var.project_id
  role    = "roles/pubsub.publisher"
  member  = "serviceAccount:service-180156150843@gs-project-accounts.iam.gserviceaccount.com"
}

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

