# HPC Monitoring

This repository configures HPC components to export performance metrics to Prometheus and visualize them in Grafana. It uses Ansible to deploy and configure exporters across your HPC environment.

## Components and Exporters

Below is a list of components and their corresponding exporters/integrations:

<table>
  <tr>
    <th>Component</th>
    <th>Exporter/Integration</th>
    <th>Purpose</th>
  </tr>
  <tr>
    <td>Compute Nodes (Rocky Linux)</td>
    <td>Node Exporter</td>
    <td>Monitor CPU, Memory, IO Wait, Storage Utilization, and Network Performance</td>
  </tr>
  <tr>
    <td>GPUs</td>
    <td>Nvidia DCGM Exporter</td>
    <td>Monitor GPU performance and related metrics</td>
  </tr>
  <tr>
    <td>Job Scheduler (SLURM)</td>
    <td>SLURM Exporter</td>
    <td>Gather HPC job and queue performance statistics</td>
  </tr>
  <tr>
    <td>Storage (WEKA Environment)</td>
    <td>WEKA Exporter</td>
    <td>Monitor storage performance and utilization</td>
  </tr>
</table>

## Repository Structure

Below is the repository structure:

<pre>
.
├── ansible
│   ├── inventory
│   ├── playbooks
│   │   ├── hpc_monitoring.yml
│   │   └── grafana_stack.yml
│   └── roles
│       ├── node_exporter
│       ├── nvidia_dcgm_exporter
│       ├── slurm_exporter
│       ├── wekafs_exporter
│       └── grafana_stack
├── docker
│   └── grafana-stack
│       └── docker-compose.yml
└── grafana_dashboards
    ├── hardware_dashboard.json
    ├── hpc_job_dashboard.json
    └── hpc_fullstack_dashboard.json
</pre>

## Usage

1. **Inventory Update:**  
   Update the `ansible/inventory` file with your target hostnames for each group (e.g., HPC clusters, GPU nodes, job scheduler, WEKA storage, and Grafana host).

2. **Customize Variables:**  
   Adjust exporter-specific variables in the defaults files under `ansible/roles/`.

3. **Deploy Monitoring Agents:**  
   Run the following playbook to deploy the monitoring agents on your HPC hosts:
   ```bash
   ansible-playbook -i ansible/inventory ansible/playbooks/hpc_monitoring.yml
