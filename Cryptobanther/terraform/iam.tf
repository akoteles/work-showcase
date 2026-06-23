locals {
  has_service_account = var.service_account_email != ""
}

resource "google_bigquery_dataset_iam_member" "raw_dataEditor" {
  count      = local.has_service_account ? 1 : 0
  dataset_id = google_bigquery_dataset.raw.dataset_id
  role       = "roles/bigquery.dataEditor"
  member     = "serviceAccount:${var.service_account_email}"
}

resource "google_bigquery_dataset_iam_member" "reporting_dataEditor" {
  count      = local.has_service_account ? 1 : 0
  dataset_id = google_bigquery_dataset.reporting.dataset_id
  role       = "roles/bigquery.dataEditor"
  member     = "serviceAccount:${var.service_account_email}"
}

resource "google_bigquery_dataset_iam_member" "logging_dataEditor" {
  count      = local.has_service_account ? 1 : 0
  dataset_id = google_bigquery_dataset.logging.dataset_id
  role       = "roles/bigquery.dataEditor"
  member     = "serviceAccount:${var.service_account_email}"
}

resource "google_project_iam_member" "bq_job_user" {
  count   = local.has_service_account ? 1 : 0
  project = var.project_id
  role    = "roles/bigquery.jobUser"
  member  = "serviceAccount:${var.service_account_email}"
}

resource "google_storage_bucket_iam_member" "staging_objectAdmin" {
  count  = local.has_service_account ? 1 : 0
  bucket = google_storage_bucket.staging.name
  role   = "roles/storage.objectAdmin"
  member = "serviceAccount:${var.service_account_email}"
}
