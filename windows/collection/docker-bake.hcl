target "presents" {
  context = "./"
  dockerfile = "Dockerfile"
  tags = ["presents:latest"]
}

group "default" {
  targets = ["presents"]
}
