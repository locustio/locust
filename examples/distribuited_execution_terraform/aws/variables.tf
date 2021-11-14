variable "node_size" {
    description = "Size of total nodes"
    default = 2
}

variable "loadtest_dir_source" {
    default = "plan/"
}

variable "locust_plan_filename" {
    default = "basic.py"
}

variable "subnet_name" {
    default = "subnet-prd-a"
    description = "Subnet name"
}
