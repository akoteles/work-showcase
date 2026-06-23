variable "project_id" {
  description = "GCP project ID"
  type        = string
}

variable "region" {
  description = "GCP region for resources"
  type        = string
  default     = "europe-west2"
}

variable "environment" {
  description = "Deployment environment (prod, staging, dev)"
  type        = string
  default     = "prod"
}

variable "bq_dataset_raw" {
  description = "BigQuery dataset for raw ingested data"
  type        = string
  default     = "raw"
}

variable "bq_dataset_reporting" {
  description = "BigQuery dataset for reporting/transformed data"
  type        = string
  default     = "reporting"
}

variable "bq_dataset_logging" {
  description = "BigQuery dataset for pipeline execution logs"
  type        = string
  default     = "logging"
}

variable "gcs_bucket_name" {
  description = "Name of the GCS staging bucket"
  type        = string
}

variable "service_account_email" {
  description = "Email of the ingestion service account"
  type        = string
  default     = ""
}
