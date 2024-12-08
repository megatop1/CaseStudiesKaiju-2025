target "puzzle" {
  context = "./"
  dockerfile = "Dockerfile"
  tags = ["puzzle:latest"]
}

group "default" {
  targets = ["puzzle"]
}
    
