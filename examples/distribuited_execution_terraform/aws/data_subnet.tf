data "aws_subnet" "current" {
    filter {
        name   = "tag:Name"
        values = [var.subnet_name]
    }
}
