terraform {
  required_version = ">= 1.2.0, < 2.0.0"
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 6.37.0"
    }
    time = {
      source  = "hashicorp/time"
      version = "~> 0.9"
    }
  }
}

provider "google" {
  credentials = file(var.gcp_auth_file)
  project     = var.project_id
  region      = var.region
}

resource "google_project_service" "required_management_apis" {
  for_each = toset([
  ])
  project = var.project_id
  service = each.value
}

resource "time_sleep" "wait_2_seconds" {
  create_duration = "2s"
  depends_on = [google_project_service.required_management_apis]
}
