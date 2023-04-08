output "leader_public_ip" {
    value = module.loadtest.leader_public_ip
    description = "The public IP address of the leader server instance."
}

output "leader_private_ip" {
    value = module.loadtest.leader_private_ip
    description = "The private IP address of the leader server instance."
}

output "nodes_public_ip" {
    value = module.loadtest.nodes_public_ip
    description = "The public IP address of the nodes instances."
}

output "nodes_private_ip" {
    value = module.loadtest.nodes_private_ip
    description = "The private IP address of the nodes instances."
}

output "dashboard_url" {
    value = "http://${coalesce(module.loadtest.leader_public_ip, module.loadtest.leader_private_ip)}"
    description = "The URL of the Locust UI."
}
