resource "google_bigquery_dataset" "raw" {
  dataset_id                  = var.bq_dataset_raw
  location                    = var.region
  description                 = "Raw ingested data from YouTube, GSC, and MySQL"
  delete_contents_on_destroy  = false

  labels = {
    environment = var.environment
    managed_by  = "terraform"
  }
}

resource "google_bigquery_dataset" "reporting" {
  dataset_id                  = var.bq_dataset_reporting
  location                    = var.region
  description                 = "Reporting and transformation layer"
  delete_contents_on_destroy  = false

  labels = {
    environment = var.environment
    managed_by  = "terraform"
  }
}

resource "google_bigquery_dataset" "logging" {
  dataset_id                  = var.bq_dataset_logging
  location                    = var.region
  description                 = "Pipeline execution logs and observability"
  delete_contents_on_destroy  = false

  labels = {
    environment = var.environment
    managed_by  = "terraform"
  }
}

resource "google_bigquery_table" "youtube_channel_stats" {
  dataset_id          = google_bigquery_dataset.raw.dataset_id
  table_id            = "youtube_channel_stats"
  deletion_protection = true

  schema = file("${path.module}/../bigquery/schemas/youtube_channel_stats.json")

  time_partitioning {
    type  = "DAY"
    field = "partition_date"
  }

  clustering = ["channel_id"]

  labels = {
    source      = "youtube"
    environment = var.environment
  }
}

resource "google_bigquery_table" "youtube_video_stats" {
  dataset_id          = google_bigquery_dataset.raw.dataset_id
  table_id            = "youtube_video_stats"
  deletion_protection = true

  schema = file("${path.module}/../bigquery/schemas/youtube_video_stats.json")

  time_partitioning {
    type  = "DAY"
    field = "partition_date"
  }

  clustering = ["channel_id", "video_id"]

  labels = {
    source      = "youtube"
    environment = var.environment
  }
}

resource "google_bigquery_table" "youtube_video_metadata" {
  dataset_id          = google_bigquery_dataset.raw.dataset_id
  table_id            = "youtube_video_metadata"
  deletion_protection = true

  schema = file("${path.module}/../bigquery/schemas/youtube_video_metadata.json")

  clustering = ["channel_id"]

  labels = {
    source      = "youtube"
    environment = var.environment
  }
}

resource "google_bigquery_table" "gsc_search_performance" {
  dataset_id          = google_bigquery_dataset.raw.dataset_id
  table_id            = "gsc_search_performance"
  deletion_protection = true

  schema = file("${path.module}/../bigquery/schemas/gsc_search_performance.json")

  time_partitioning {
    type  = "DAY"
    field = "partition_date"
  }

  clustering = ["site_url"]

  labels = {
    source      = "gsc"
    environment = var.environment
  }
}

resource "google_bigquery_table" "pipeline_execution_logs" {
  dataset_id          = google_bigquery_dataset.logging.dataset_id
  table_id            = "pipeline_execution_logs"
  deletion_protection = false

  schema = file("${path.module}/../bigquery/schemas/pipeline_execution_logs.json")

  time_partitioning {
    type  = "DAY"
    field = "execution_date"
  }

  clustering = ["dag_id", "source_system"]

  labels = {
    purpose     = "observability"
    environment = var.environment
  }
}
