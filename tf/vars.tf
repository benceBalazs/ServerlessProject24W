variable "project_id" {
  description = "The GCP project ID of the serverless project 24W"
  type        = string
  default     = "serverless-project-24w"
}

variable "region" {
  description = "Deployment Region of the project"
  type        = string
  default     = "europe-west1"
}

locals {
  function_config = var.test_config_1
}

variable "test_config_1" {
  default = {
    exif_processor = {
      max_instance_count = 100
      min_instance_count = 1
      available_memory   = "256Mi"
      timeout_seconds    = 60
    }

    format_converter = {
      max_instance_count = 100
      min_instance_count = 1
      available_memory   = "256Mi"
      timeout_seconds    = 60
    }

    input_handler = {
      max_instance_count = 100
      min_instance_count = 1
      available_memory   = "256Mi"
      timeout_seconds    = 60
    }

    metadata_extractor = {
      max_instance_count = 100
      min_instance_count = 1
      available_memory   = "256Mi"
      timeout_seconds    = 60
    }

    rgb_channel_separator = {
      max_instance_count = 100
      min_instance_count = 1
      available_memory   = "256Mi"
      timeout_seconds    = 60
    }

    thumbnail_generator = {
      max_instance_count = 100
      min_instance_count = 1
      available_memory   = "256Mi"
      timeout_seconds    = 60
    }
  }
}
