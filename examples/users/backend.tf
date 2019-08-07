terraform {
    backend "s3" {
    bucket = "cs-comet-test-state"
    key    = "users/us-west-2"
    region = "us-west-2"
    role_arn= "arn:aws:iam::867580301722:role/terraform"
    profile  = "codesherpas"
    }
}

