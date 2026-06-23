output "raw_dataset_id" {
  description = "BigQuery raw dataset ID"
  value       = google_bigquery_dataset.raw.dataset_id
}

output "reporting_dataset_id" {
  description = "BigQuery reporting dataset ID"
  value       = google_bigquery_dataset.reporting.dataset_id
}

output "logging_dataset_id" {
  description = "BigQuery logging dataset ID"
  value       = google_bigquery_dataset.logging.dataset_id
}

output "staging_bucket_name" {
  description = "GCS staging bucket name"
  value       = google_storage_bucket.staging.name
}

output "staging_bucket_url" {
  description = "GCS staging bucket URL"
  value       = google_storage_bucket.staging.url
}
