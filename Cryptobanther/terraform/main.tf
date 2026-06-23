terraform {
  required_version = ">= 1.5"
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
  }
  backend "gcs" {
    # Configure via -backend-config flags or terraform.tfbackend
    # bucket = "your-terraform-state-bucket"
    # prefix = "cryptobanter-gcp-data-platform"
  }
}

provider "google" {
  project = var.project_id
  region  = var.region
}
