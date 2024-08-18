variable "project" {}
variable "bucket_name" {}
variable "bucket_location" {}

provider "google" {
  project = var.project
}

resource "google_storage_bucket" "gcp_bucket" {
  name          = var.bucket_name
  location      = var.bucket_location
}