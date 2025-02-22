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
