variable "project_id" {
  description = "The GCP project ID of the serverless project 24W"
  type = string
}

variable "region" {
  description = "Deployment Region of the project"
  type = string
  default = "europe-west1"
}

variable "function_memory" {
  description = "Necessary Memory allocation for Cloud Functions"
  type = map(string)
  default = {
    "input_handler" = "256MB"
    "metadata_extractor" = "512MB"
    "exif_processor" = "256MB"
    "format_converter" = "512MB"
    "thumbnail_generator" = "512MB"
    "rgb_channel_separator" = "512MB"
    "metrics_visualizer" = "256MB"
  }
}

variable "function_timeout" {
  description = "Timeout for Cloud Functions"
  type = map(number)
  default = {
    "input_handler" = 60
    "metadata_extractor" = 120
    "exif_processor" = 60
    "format_converter" = 120
    "thumbnail_generator" = 120
    "rgb_channel_separator" = 120
    "metrics_visualizer"  = 120
  }
}