.. _running-cloud-integration:

======================================================
Running Locust Distributed with IaC on IaaS (AWS/EC2)
======================================================

Here we have an example of infrastructure provisioning for load test execution in a distributed way using the IaC concept.

For this we use a terraform module that performs the provisioning of 1 leader and "n" nodes to perform the load. Provisioning is performed on the AWS Cloud and we use the EC2 service.

At the end of provisioning you have access to the locust UI url.

The prerequisites are:

- Have the terraform installed;
- Have AWS access keys;
- Configure the subnet;
- Configure the location of your test script;
- Define the number of workers (nodes) to be created;


More information
===================

- :ref:`Example <https://github.com/locustio/locust/blob/master/examples/terraform/aws/README.md>`

- :ref:`Terraform aws-get-started >> install-terraform-on-linux <https://learn.hashicorp.com/tutorials/terraform/install-cli?in=terraform/aws-get-started#install-terraform-on-linux>`

- :ref:`Terraform module aws loadtest distributed <https://registry.terraform.io/modules/marcosborges/loadtest-distribuited/aws/latest>`

