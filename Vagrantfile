Vagrant.configure("2") do |config|
  config.vm.box = "ubuntu/xenial32"
  config.vm.network :forwarded_port, guest: 8089, host: 8089
  config.vm.provision :shell, :path => "examples/vagrant/vagrant.sh"
end
