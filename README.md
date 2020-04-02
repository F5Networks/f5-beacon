# Ansible Collection - f5networks.f5_beacon

This collection is used to configure the F5 Beacon SaaS offering.

## Introduction
Beacon enables IT leaders and operators to achieve full visibility across their application landscape through insights, application health, dashboards, and more.

## Requirements
  - Subscription to F5 Beacon ([Register Here](https://beacon.f5.com/register))
  - Ansible >= 2.9

## Documentation
For an overview of Beacon in general please check our hosted [Documentation Page](https://clouddocs.f5.com/cloud-services/latest/f5-cloud-services-Beacon-About.html).  

### Example Playbook
Ansible modules are documented within each module itself. The example below will create a Token, check for existing data, create an application

```
---
- name: Configure Beacon
  hosts: beacon
  gather_facts: false
  connection: httpapi
  collections:
    - f5networks.f5_beacon


  vars:
    ansible_host: "api.cloudservices.f5.com"
    ansible_user: "username"
    ansible_httpapi_password: "password"
    ansible_network_os: f5networks.f5_beacon.f5
    ansible_httpapi_use_ssl: yes
    cur_state: present

  tasks:

    # Create Token for Data Sources
    - name: Beacon Token
      beacon_token:
        name: "ExampleToken"
        preferred_account_id: "{{ account_id }}"
        description: "Ansible Token"
        state: "{{ cur_state }}"
    
    # Gather Information about Beacon
    - name: Collect Beacon Information
      beacon_info:
        preferred_account_id: "{{ account_id }}"
        gather_subset:
          - tokens
          - sources
      register: beacon_info

    # Create Application declaration on Beacon
    - name: Application Declaration
      beacon_declaration:
        preferred_account_id: "{{ account_id }}"
        content: "{{ lookup('file', 'decl.json') }}"
        state: "{{ cur_state }}"
```

**IMPORTANT** Please note that the declaration that the Collection expects is only the declaration array object surrounded by `{}`. Beacon handles the deploy/delete objects for you. An example of the input is below.

Example `decl.json`
```
{
    "declaration": [
        {
            "metadata": {
                "Version": "v1",
                "Operation": ""
            },
            "application": {
                "name": "API-Demo-App-5",
                "description": "An example for a Beacon application",
                ...
            }
        }
    ]
}
```

### Installation
To install in ansible default or defined paths use:

```ansible-galaxy collection install f5networks.f5_beacon```

To specify the installation location use -p. If specifying a folder, make sure to update the ansible.cfg so ansible will check this folder as well.

```ansible-galaxy collection install f5networks.f5_beacon -p collections/```

To specify the version of the collection to install, include it at the end of the collection with :==1.0.0:

```ansible-galaxy collection install f5networks.f5_beacon:==1.0.0```



## Filing Issues
If you come across a bug or other issue when using the F5 Beacon Collection, use [GitHub Issues](https://github.com/f5networks/f5-beacon/issues) to submit an issue for our team.
