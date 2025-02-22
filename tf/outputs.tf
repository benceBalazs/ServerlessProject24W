output "input_bucket_name" {
  description = "The name of the input bucket"
  value       = data.google_storage_bucket.input_bucket.name
}

output "output_bucket_name" {
  description = "The name of the output bucket"
  value       = data.google_storage_bucket.output_bucket.name
}

output "function_urls" {
  description = "The URLs of the deployed Cloud Functions"
  value = {
    input_handler         = google_cloudfunctions2_function.input_handler.url
    metadata_extractor    = google_cloudfunctions2_function.metadata_extractor.url
    exif_processor        = google_cloudfunctions2_function.exif_processor.url
    format_converter      = google_cloudfunctions2_function.format_converter.url
    rgb_channel_separator = google_cloudfunctions2_function.rgb_channel_separator.url
    thumbnail_generator   = google_cloudfunctions2_function.thumbnail_generator.url
  }
}
