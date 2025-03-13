# HPC Monitoring Stack

## Overview
This repository contains the HPC Monitoring Stack for monitoring compute nodes, GPUs, job schedulers, storage, and networking.

## Deployment Instructions
1. Clone this repository:
   ```bash
   git clone git@github.com:pdgeek-io/hpc-monitoring.git
   cd hpc-monitoring
   ```
2. Deploy the monitoring stack:
   ```bash
   ansible-playbook -i ansible/inventory playbooks/deploy_hpc_monitoring.yml
   ```
