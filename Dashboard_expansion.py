import os

# Dictionary mapping file paths to their content.
# This includes the updated inventory file and three new Grafana dashboards.
files = {
    # Updated inventory file with HPC cluster groups
    "ansible/inventory": r"""[hpc1]
rocky1.example.com
rocky2.example.com

[hpc2]
rocky3.example.com
rocky4.example.com

[gpu_nodes]
gpu1.example.com

[job_scheduler]
scheduler.example.com

[storage_weka]
weka1.example.com
""",
    # Updated playbook (if needed) – here we assume the playbook remains similar,
    # but you might customize roles per group if desired.
    "ansible/playbooks/hpc_monitoring.yml": r"""---
- name: Configure HPC1 and HPC2 Compute Nodes with Node Exporter
  hosts: hpc1:hpc2
  become: yes
  roles:
    - node_exporter

- name: Configure GPU Nodes with Nvidia DCGM Exporter
  hosts: gpu_nodes
  become: yes
  roles:
    - nvidia_dcgm_exporter

- name: Configure SLURM Job Scheduler
  hosts: job_scheduler
  become: yes
  roles:
    - slurm_exporter

- name: Configure WEKA Environment Exporter
  hosts: storage_weka
  become: yes
  roles:
    - wekafs_exporter
""",
    # Grafana dashboard: Hardware Dashboard monitoring per HPC cluster
    "grafana_dashboards/hardware_dashboard.json": r"""{
  "annotations": {
    "list": []
  },
  "editable": true,
  "gnetId": null,
  "graphTooltip": 0,
  "id": null,
  "links": [],
  "panels": [
    {
      "datasource": "Prometheus",
      "fieldConfig": { "defaults": { "unit": "percent" }, "overrides": [] },
      "gridPos": { "h": 8, "w": 12, "x": 0, "y": 0 },
      "id": 1,
      "title": "HPC1 - CPU Usage",
      "type": "graph",
      "targets": [
        { "expr": "100 - (avg by(instance)(irate(node_cpu_seconds_total{mode=\"idle\", cluster=\"hpc1\"}[5m])) * 100)", "legendFormat": "{{instance}}", "refId": "A" }
      ]
    },
    {
      "datasource": "Prometheus",
      "fieldConfig": { "defaults": { "unit": "percent" }, "overrides": [] },
      "gridPos": { "h": 8, "w": 12, "x": 12, "y": 0 },
      "id": 2,
      "title": "HPC1 - Memory Usage",
      "type": "graph",
      "targets": [
        { "expr": "(1 - (node_memory_MemAvailable_bytes{cluster=\"hpc1\"} / node_memory_MemTotal_bytes{cluster=\"hpc1\"})) * 100", "legendFormat": "{{instance}}", "refId": "B" }
      ]
    },
    {
      "datasource": "Prometheus",
      "fieldConfig": { "defaults": { "unit": "Bps" }, "overrides": [] },
      "gridPos": { "h": 8, "w": 12, "x": 0, "y": 8 },
      "id": 3,
      "title": "HPC1 - Network Throughput",
      "type": "graph",
      "targets": [
        { "expr": "irate(node_network_transmit_bytes_total{cluster=\"hpc1\"}[5m])", "legendFormat": "{{instance}} tx", "refId": "C" }
      ]
    },
    {
      "datasource": "Prometheus",
      "fieldConfig": { "defaults": { "unit": "percent" }, "overrides": [] },
      "gridPos": { "h": 8, "w": 12, "x": 12, "y": 8 },
      "id": 4,
      "title": "HPC1 - Storage Utilization",
      "type": "graph",
      "targets": [
        { "expr": "100 - (node_filesystem_free_bytes{cluster=\"hpc1\"} / node_filesystem_size_bytes{cluster=\"hpc1\"} * 100)", "legendFormat": "{{mountpoint}}", "refId": "D" }
      ]
    },
    {
      "datasource": "Prometheus",
      "fieldConfig": { "defaults": { "unit": "percent" }, "overrides": [] },
      "gridPos": { "h": 8, "w": 12, "x": 0, "y": 16 },
      "id": 5,
      "title": "HPC2 - CPU Usage",
      "type": "graph",
      "targets": [
        { "expr": "100 - (avg by(instance)(irate(node_cpu_seconds_total{mode=\"idle\", cluster=\"hpc2\"}[5m])) * 100)", "legendFormat": "{{instance}}", "refId": "E" }
      ]
    },
    {
      "datasource": "Prometheus",
      "fieldConfig": { "defaults": { "unit": "percent" }, "overrides": [] },
      "gridPos": { "h": 8, "w": 12, "x": 12, "y": 16 },
      "id": 6,
      "title": "HPC2 - Memory Usage",
      "type": "graph",
      "targets": [
        { "expr": "(1 - (node_memory_MemAvailable_bytes{cluster=\"hpc2\"} / node_memory_MemTotal_bytes{cluster=\"hpc2\"})) * 100", "legendFormat": "{{instance}}", "refId": "F" }
      ]
    }
  ],
  "schemaVersion": 30,
  "style": "dark",
  "tags": ["hardware", "hpc", "cluster"],
  "templating": { "list": [] },
  "time": { "from": "now-12h", "to": "now" },
  "timezone": "",
  "title": "Hardware Dashboard - HPC Clusters",
  "uid": "hardware-dashboard",
  "version": 1
}""",
    # Grafana dashboard: HPC JOB Dashboard
    "grafana_dashboards/hpc_job_dashboard.json": r"""{
  "annotations": {
    "list": []
  },
  "editable": true,
  "gnetId": null,
  "graphTooltip": 0,
  "id": null,
  "links": [],
  "panels": [
    {
      "datasource": "Prometheus",
      "fieldConfig": { "defaults": { "unit": "none" }, "overrides": [] },
      "gridPos": { "h": 8, "w": 12, "x": 0, "y": 0 },
      "id": 1,
      "title": "SLURM Job Queue Length",
      "type": "graph",
      "targets": [
        { "expr": "slurm_job_queue_length", "legendFormat": "{{cluster}}", "refId": "A" }
      ]
    },
    {
      "datasource": "Prometheus",
      "fieldConfig": { "defaults": { "unit": "s" }, "overrides": [] },
      "gridPos": { "h": 8, "w": 12, "x": 12, "y": 0 },
      "id": 2,
      "title": "Average Job Run Time",
      "type": "graph",
      "targets": [
        { "expr": "avg(slurm_job_run_time_seconds)", "legendFormat": "{{cluster}}", "refId": "B" }
      ]
    }
  ],
  "schemaVersion": 30,
  "style": "dark",
  "tags": ["jobs", "slurm", "hpc"],
  "templating": { "list": [] },
  "time": { "from": "now-12h", "to": "now" },
  "timezone": "",
  "title": "HPC JOB Dashboard",
  "uid": "job-dashboard",
  "version": 1
}""",
    # Grafana dashboard: HPC Full Stack Monitor (combines hardware and job stats)
    "grafana_dashboards/hpc_fullstack_dashboard.json": r"""{
  "annotations": {
    "list": []
  },
  "editable": true,
  "gnetId": null,
  "graphTooltip": 0,
  "id": null,
  "links": [],
  "panels": [
    {
      "datasource": "Prometheus",
      "fieldConfig": { "defaults": { "unit": "percent" }, "overrides": [] },
      "gridPos": { "h": 8, "w": 12, "x": 0, "y": 0 },
      "id": 1,
      "title": "HPC1 - CPU Usage",
      "type": "graph",
      "targets": [
        { "expr": "100 - (avg by(instance)(irate(node_cpu_seconds_total{mode=\"idle\", cluster=\"hpc1\"}[5m])) * 100)", "legendFormat": "{{instance}}", "refId": "A" }
      ]
    },
    {
      "datasource": "Prometheus",
      "fieldConfig": { "defaults": { "unit": "none" }, "overrides": [] },
      "gridPos": { "h": 8, "w": 12, "x": 12, "y": 0 },
      "id": 2,
      "title": "SLURM Job Queue",
      "type": "graph",
      "targets": [
        { "expr": "slurm_job_queue_length", "legendFormat": "{{cluster}}", "refId": "B" }
      ]
    },
    {
      "datasource": "Prometheus",
      "fieldConfig": { "defaults": { "unit": "Bps" }, "overrides": [] },
      "gridPos": { "h": 8, "w": 12, "x": 0, "y": 8 },
      "id": 3,
      "title": "Network Throughput",
      "type": "graph",
      "targets": [
        { "expr": "irate(node_network_transmit_bytes_total[5m])", "legendFormat": "{{instance}} tx", "refId": "C" }
      ]
    },
    {
      "datasource": "Prometheus",
      "fieldConfig": { "defaults": { "unit": "s" }, "overrides": [] },
      "gridPos": { "h": 8, "w": 12, "x": 12, "y": 8 },
      "id": 4,
      "title": "Average Job Run Time",
      "type": "graph",
      "targets": [
        { "expr": "avg(slurm_job_run_time_seconds)", "legendFormat": "{{cluster}}", "refId": "D" }
      ]
    }
  ],
  "schemaVersion": 30,
  "style": "dark",
  "tags": ["full-stack", "hardware", "jobs", "hpc"],
  "templating": { "list": [] },
  "time": { "from": "now-12h", "to": "now" },
  "timezone": "",
  "title": "HPC Full Stack Monitor",
  "uid": "fullstack-dashboard",
  "version": 1
}"""
}

def create_files():
    for filepath, content in files.items():
        directory = os.path.dirname(filepath)
        if directory and not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)
        with open(filepath, "w") as f:
            f.write(content)
        print(f"Created/Updated: {filepath}")

if __name__ == "__main__":
    create_files()
    print("Repository folders, host structure, and Grafana dashboards have been updated.")
