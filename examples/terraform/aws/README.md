
## 1. AWS Authentication

```bash
export AWS_ACCESS_KEY_ID=AIAXXXXXXXXXXXXXXXXX
export AWS_SECRET_ACCESS_KEY=T9HyXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

## 2. Configure your provisioning

- Don't forget to provide the correct subnet name in the variable file
- Define location and file of your locust plan script
- Define the number of nodes to create

**variables.tf**

```bash
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

```



---

## 3. Execute Terraform

```bash
cd examples/terraform/aws
terraform init
terraform apply --auto-approve
```

---

## 4. Access UI

Click on the link below to access the UI:

Result exemple:

```bash
Apply complete! Resources: 14 added, 0 changed, 0 destroyed.

Outputs:

dashboard_url = "http://3.237.255.123"
leader_private_ip = "10.17.5.119"
leader_public_ip = "3.237.255.123"
nodes_private_ip = [
  "10.17.5.167",
  "10.17.5.39",
]
nodes_public_ip = [
  "3.235.45.218",
  "100.24.124.0",
]
```

![locust-home](https://github.com/marcosborges/terraform-aws-loadtest-distribuited/raw/v0.4.0/assets/locust-home.png)

---

## 5. Cleanup

```bash
terraform destroy --auto-approve
```

---

## 6. More information

- [Terraform aws-get-started >> install-terraform-on-linux](https://learn.hashicorp.com/tutorials/terraform/install-cli?in=terraform/aws-get-started#install-terraform-on-linux)

- [Terraform module aws loadtest distribuited](https://registry.terraform.io/modules/marcosborges/loadtest-distribuited/aws/latest)

