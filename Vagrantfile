# -*- mode: ruby -*-
# vi: set ft=ruby :

# vagrant up --provision-with "conf_int"
# 00:0c:29:ca:d4:01
# host R1 {
#   hardware ethernet 00:0c:29:ca:d4:01;
#   fixed-address 172.16.55.11;
# }


Vagrant.configure("2") do |config|
  
  config.vm.provision "conf_int", type: "ansible" do |ansible|
     ansible.playbook = "vagrant-vios.yml"
     ansible.compatibility_mode = "2.0"
     ansible.tags = "conf_int"
   end

  config.vm.provision "conf_cdp", type: "ansible" do |ansible|
     ansible.playbook = "vagrant-vios.yml"
     ansible.compatibility_mode = "2.0"
          ansible.tags = "conf_cdp"
   end


  config.vm.provision "ping_int", type: "ansible" do |ansible|
     ansible.playbook = "vagrant-vios.yml"
     ansible.compatibility_mode = "2.0"
          ansible.tags = "ping_int"
   end

  config.vm.provision "ping_loop", type: "ansible" do |ansible|
     ansible.playbook = "vagrant-vios.yml"
     ansible.compatibility_mode = "2.0"
          ansible.tags = "ping_loop"
   end

  config.vm.provision "int_reset", type: "ansible" do |ansible|
     ansible.playbook = "vagrant-vios.yml"
     ansible.compatibility_mode = "2.0"
          ansible.tags = "int_reset"
   end


  config.vm.define "R1" do |node|
    node.ssh.insert_key = false
    # node.ssh.host = '172.16.55.11'
    node.vm.box = "cisco-iosv-l3-156-2"
    node.vm.boot_timeout = 90
    # Disable default host <-> guest synced folder
    node.vm.synced_folder ".", "/vagrant", disabled: true
    # Set guest OS type to disable autodetection
    node.vm.guest = :freebsd
    # Disable port forwarding for SSH
#    node.vm.network 'private_network', type: dhcp
    # node.vm.network 'private_network', ip: '10.120.10.200'
    node.vm.network :forwarded_port, guest: 22, host: 2201, id: "ssh", disabled: true

    node.vm.provider :vmware_desktop do |v|
      # v.vmx['ethernet0.addressType'] = "static"
      # v.vmx['ethernet0.generatedAddress'] = "nil"
      # v.vmx['ethernet0.present'] = "TRUE"
      # v.vmx['ethernet0.address'] = "00:0c:29:ca:d4:01"

      v.vmx['ethernet1.connectionType'] = "custom"
      v.vmx['ethernet1.vnet'] = "vmnet10"
      v.vmx['ethernet1.addressType'] = "generated"
      v.vmx['ethernet1.virtualDev'] = "e1000"
      v.vmx['ethernet1.present'] = "TRUE"
      v.vmx['ethernet2.connectionType'] = "custom"
      v.vmx['ethernet2.vnet'] = "vmnet13"
      v.vmx['ethernet2.addressType'] = "generated"
      v.vmx['ethernet2.virtualDev'] = "e1000"
      v.vmx['ethernet2.present'] = "TRUE"
      # https://www.vagrantup.com/docs/vmware/configuration.html#linked_clone
      v.linked_clone = false
      # https://www.vagrantup.com/docs/vmware/boxes.html#vmx-whitelisting
      v.whitelist_verified = true
      # https://www.vagrantup.com/docs/vmware/configuration.html#ssh_info_public
      v.ssh_info_public = true
      # Console port connection via telnet (or netcat)
      v.vmx["serial0.fileName"] = "telnet://127.0.0.1:52001"
    end
  end

  config.vm.define "R2" do |node|
    node.ssh.insert_key = false
    node.vm.box = "cisco-iosv-l3-156-2"
    node.vm.boot_timeout = 90
    # Disable default host <-> guest synced folder
    node.vm.synced_folder ".", "/vagrant", disabled: true
    # Set guest OS type to disable autodetection
    node.vm.guest = :freebsd
    # Disable port forwarding for SSH
    node.vm.network :forwarded_port, guest: 22, host: 2202, id: "ssh", disabled: true
#    node.vm.network 'private_network', type: dhcp
#    node.vm.network 'private_network', type: dhcp

    node.vm.provider :vmware_desktop do |v|
      v.vmx['ethernet1.connectionType'] = "custom"
      v.vmx['ethernet1.vnet'] = "vmnet10"
      v.vmx['ethernet1.addressType'] = "generated"
      v.vmx['ethernet1.virtualDev'] = "e1000"
      v.vmx['ethernet1.present'] = "TRUE"

      v.vmx['ethernet2.connectionType'] = "custom"
      v.vmx['ethernet2.vnet'] = "vmnet11"
      v.vmx['ethernet2.addressType'] = "generated"
      v.vmx['ethernet2.virtualDev'] = "e1000"
      v.vmx['ethernet2.present'] = "TRUE"

      v.vmx['ethernet3.connectionType'] = "custom"
      v.vmx['ethernet3.vnet'] = "vmnet14"
      v.vmx['ethernet3.addressType'] = "generated"
      v.vmx['ethernet3.virtualDev'] = "e1000"
      v.vmx['ethernet3.present'] = "TRUE"

      # https://www.vagrantup.com/docs/vmware/configuration.html#linked_clone
      v.linked_clone = false
      # https://www.vagrantup.com/docs/vmware/boxes.html#vmx-whitelisting
      v.whitelist_verified = true
      # https://www.vagrantup.com/docs/vmware/configuration.html#ssh_info_public
      v.ssh_info_public = true
      # Console port connection via telnet (or netcat)
      v.vmx["serial0.fileName"] = "telnet://127.0.0.1:52002"
    end
  end

  config.vm.define "R3" do |node|
    node.ssh.insert_key = false
    node.vm.box = "cisco-iosv-l3-156-2"
    node.vm.boot_timeout = 90
    # Disable default host <-> guest synced folder
    node.vm.synced_folder ".", "/vagrant", disabled: true
    # Set guest OS type to disable autodetection
    node.vm.guest = :freebsd
    # Disable port forwarding for SSH
    node.vm.network :forwarded_port, guest: 22, host: 2203, id: "ssh", disabled: true
#    node.vm.network 'private_network', type: dhcp
#    node.vm.network 'private_network', type: dhcp

    node.vm.provider :vmware_desktop do |v|
      v.vmx['ethernet1.connectionType'] = "custom"
      v.vmx['ethernet1.vnet'] = "vmnet12"
      v.vmx['ethernet1.addressType'] = "generated"
      v.vmx['ethernet1.virtualDev'] = "e1000"
      v.vmx['ethernet1.present'] = "TRUE"

      v.vmx['ethernet2.connectionType'] = "custom"
      v.vmx['ethernet2.vnet'] = "vmnet11"
      v.vmx['ethernet2.addressType'] = "generated"
      v.vmx['ethernet2.virtualDev'] = "e1000"
      v.vmx['ethernet2.present'] = "TRUE"

      v.vmx['ethernet3.connectionType'] = "custom"
      v.vmx['ethernet3.vnet'] = "vmnet15"
      v.vmx['ethernet3.addressType'] = "generated"
      v.vmx['ethernet3.virtualDev'] = "e1000"
      v.vmx['ethernet3.present'] = "TRUE"

      # https://www.vagrantup.com/docs/vmware/configuration.html#linked_clone
      v.linked_clone = false
      # https://www.vagrantup.com/docs/vmware/boxes.html#vmx-whitelisting
      v.whitelist_verified = true
      # https://www.vagrantup.com/docs/vmware/configuration.html#ssh_info_public
      v.ssh_info_public = true
      # Console port connection via telnet (or netcat)
      v.vmx["serial0.fileName"] = "telnet://127.0.0.1:52003"
    end
  end

  config.vm.define "R4" do |node|
    node.ssh.insert_key = false
    node.vm.box = "cisco-iosv-l3-156-2"
    node.vm.boot_timeout = 90
    # Disable default host <-> guest synced folder
    node.vm.synced_folder ".", "/vagrant", disabled: true
    # Set guest OS type to disable autodetection
    node.vm.guest = :freebsd
    # Disable port forwarding for SSH
    node.vm.network :forwarded_port, guest: 22, host: 2204, id: "ssh", disabled: true
#    node.vm.network 'private_network', type: dhcp
#    node.vm.network 'private_network', type: dhcp

    node.vm.provider :vmware_desktop do |v|
      v.vmx['ethernet1.connectionType'] = "custom"
      v.vmx['ethernet1.vnet'] = "vmnet12"
      v.vmx['ethernet1.addressType'] = "generated"
      v.vmx['ethernet1.virtualDev'] = "e1000"
      v.vmx['ethernet1.present'] = "TRUE"

      v.vmx['ethernet2.connectionType'] = "custom"
      v.vmx['ethernet2.vnet'] = "vmnet13"
      v.vmx['ethernet2.addressType'] = "generated"
      v.vmx['ethernet2.virtualDev'] = "e1000"
      v.vmx['ethernet2.present'] = "TRUE"

      v.vmx['ethernet3.connectionType'] = "custom"
      v.vmx['ethernet3.vnet'] = "vmnet14"
      v.vmx['ethernet3.addressType'] = "generated"
      v.vmx['ethernet3.virtualDev'] = "e1000"
      v.vmx['ethernet3.present'] = "TRUE"

      # https://www.vagrantup.com/docs/vmware/configuration.html#linked_clone
      v.linked_clone = false
      # https://www.vagrantup.com/docs/vmware/boxes.html#vmx-whitelisting
      v.whitelist_verified = true
      # https://www.vagrantup.com/docs/vmware/configuration.html#ssh_info_public
      v.ssh_info_public = true
      # Console port connection via telnet (or netcat)
      v.vmx["serial0.fileName"] = "telnet://127.0.0.1:52004"
    end

  end

  config.vm.define "R5" do |node|
    node.ssh.insert_key = false
    node.vm.box = "cisco-iosv-l3-156-2"
    node.vm.boot_timeout = 90
    # Disable default host <-> guest synced folder
    node.vm.synced_folder ".", "/vagrant", disabled: true
    # Set guest OS type to disable autodetection
    node.vm.guest = :freebsd
    # Disable port forwarding for SSH
    node.vm.network :forwarded_port, guest: 22, host: 2205, id: "ssh", disabled: true
#    node.vm.network 'private_network', type: dhcp
#    node.vm.network 'private_network', type: dhcp

    node.vm.provider :vmware_desktop do |v|
      v.vmx['ethernet1.connectionType'] = "custom"
      v.vmx['ethernet1.vnet'] = "vmnet15"
      v.vmx['ethernet1.addressType'] = "generated"
      v.vmx['ethernet1.virtualDev'] = "e1000"
      v.vmx['ethernet1.present'] = "TRUE"
      # https://www.vagrantup.com/docs/vmware/configuration.html#linked_clone
      v.linked_clone = false
      # https://www.vagrantup.com/docs/vmware/boxes.html#vmx-whitelisting
      v.whitelist_verified = true
      # https://www.vagrantup.com/docs/vmware/configuration.html#ssh_info_public
      v.ssh_info_public = true
      # Console port connection via telnet (or netcat)
      v.vmx["serial0.fileName"] = "telnet://127.0.0.1:52005"
    end

  end


end

