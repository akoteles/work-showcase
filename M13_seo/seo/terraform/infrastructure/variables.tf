variable "project_id" {
  description = "GCP Project ID"
  type        = string
}

variable "region" {
  description = "GCP Region"
  type        = string
  default     = "europe-west3"
}

variable "gcp_auth_file" {
  type        = string
  description = "GCP authentication file"
}

variable "env" {
  description = "Environment name"
  type        = string
}
