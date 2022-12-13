.. _running-cloud-integration:

=============================================
Running Locust distributed with Terraform/AWS
=============================================

Here's one way to provision Locust using Infrastructure as Code/IaC.

For this we use a `Terraform <https://www.terraform.io/>`_ module that provisions 1 leader and "n" worker nodes. This implementation uses AWS and EC2, but you may be able to modify it for other cloud providers.

1. `Install terraform <https://learn.hashicorp.com/tutorials/terraform/install-cli?in=terraform/aws-get-started#install-terraform-on-linux>`_
2. `Follow the README <https://github.com/locustio/locust/blob/master/examples/terraform/aws/README.md>`_
3. Further reading: `Underlying Terraform module <https://registry.terraform.io/modules/marcosborges/loadtest-distribuited/aws/latest>`_
