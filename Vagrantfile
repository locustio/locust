Vagrant::Config.run do |config|
  config.vm.box = "precise64"
  config.vm.box_url = "http://files.vagrantup.com/precise64.box"
  config.vm.forward_port 8089, 8089
  config.vm.forward_port 9001, 9001
#  config.vm.provision :shell, :path => "examples/vagrant/vagrant.sh"
end
