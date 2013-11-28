Vagrant.configure("2") do |config|
  config.vm.box = "precise32"
  config.vm.box_url = "http://files.vagrantup.com/precise32.box"
  config.vm.network :forwarded_port, guest: 8089, host: 8089
  config.vm.provision :shell, :path => "examples/vagrant/vagrant.sh"
end