variable "project_id" {
  description = "The GCP project ID of the serverless project 24W"
  type = string
  default = "serverless-project-24w"
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
    "input_handler" = "256Mi"
    "metadata_extractor" = "512Mi"
    "exif_processor" = "256Mi"
    "format_converter" = "1024Mi"
    "thumbnail_generator" = "512Mi"
    "rgb_channel_separator" = "1024Mi"
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
  }
}

variable "pubsub_topics"{
  description = "Pub/Sub topics for triggering functions"
  type = map(string)
  default = {
    "input_handler" = "input-handler-topic"
    "metadata_extractor" = "metadata-extractor-topic"
    "exif_processor" = "exif-processor-topic"
    "format_converter" = "format-converter-topic"
    "thumbnail_generator" = "thumbnail-generator-topic"
    "rgb_channel_separator" = "rgb-channel-separator-topic"
    "metrics_visualizer" = "metrics-visualizer-topic"
  }
}






