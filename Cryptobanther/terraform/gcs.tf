resource "google_storage_bucket" "staging" {
  name          = var.gcs_bucket_name
  location      = var.region
  storage_class = "STANDARD"

  uniform_bucket_level_access = true

  versioning {
    enabled = false
  }

  lifecycle_rule {
    condition {
      age            = 30
      matches_prefix = ["tmp/", "_tmp_"]
    }
    action {
      type = "Delete"
    }
  }

  lifecycle_rule {
    condition {
      age            = 90
      matches_prefix = ["staging/"]
    }
    action {
      type = "Delete"
    }
  }

  labels = {
    environment = var.environment
    managed_by  = "terraform"
    purpose     = "data-staging"
  }
}
