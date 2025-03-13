import os
import shutil

# Dictionary mapping file paths to their updated content.
# These files include updated Ansible role defaults and tasks,
# along with an updated Grafana dashboard JSON.
files = {
    "ansible/inventory": r"""[compute_nodes]
rocky1.example.com
rocky2.example.com

[gpu_nodes]
gpu1.example.com

[job_scheduler]
scheduler.example.com

[storage_weka]
weka1.example.com
""",
    "ansible/playbooks/hpc_monitoring.yml": r"""---
- name: Configure Rocky Linux Compute Nodes with Node Exporter
  hosts: compute_nodes
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
    # Node Exporter for Rocky Linux (CPU, Memory, IO Wait, Storage, Network)
    "ansible/roles/node_exporter/defaults/main.yml": r"""# Rocky Linux Node Exporter settings
node_exporter_version: "1.5.0"
node_exporter_download_url: "https://github.com/prometheus/node_exporter/releases/download/v{{ node_exporter_version }}/node_exporter-{{ node_exporter_version }}.linux-amd64.tar.gz"
node_exporter_install_dir: "/usr/local/bin"
node_exporter_user: "node_exporter"
node_exporter_port: 9100
""",
    "ansible/roles/node_exporter/tasks/main.yml": r"""---
- name: Ensure node_exporter user exists
  user:
    name: "{{ node_exporter_user }}"
    system: yes
    shell: /sbin/nologin

- name: Download node_exporter
  get_url:
    url: "{{ node_exporter_download_url }}"
    dest: "/tmp/node_exporter.tar.gz"
    mode: '0644'
  register: download_result

- name: Extract node_exporter binary
  unarchive:
    src: "/tmp/node_exporter.tar.gz"
    dest: "/tmp/"
    remote_src: yes
  when: download_result.changed

- name: Move node_exporter binary to install directory
  copy:
    src: "/tmp/node_exporter-{{ node_exporter_version }}.linux-amd64/node_exporter"
    dest: "{{ node_exporter_install_dir }}/node_exporter"
    mode: '0755'
  when: download_result.changed

- name: Deploy systemd service for node_exporter
  template:
    src: "node_exporter.service.j2"
    dest: "/etc/systemd/system/node_exporter.service"
    mode: '0644'

- name: Reload systemd daemon
  command: systemctl daemon-reload

- name: Enable and start node_exporter service
  systemd:
    name: node_exporter
    enabled: yes
    state: started
""",
    "ansible/roles/node_exporter/templates/node_exporter.service.j2": r"""[Unit]
Description=Prometheus Node Exporter (Rocky Linux)
After=network.target

[Service]
User={{ node_exporter_user }}
ExecStart={{ node_exporter_install_dir }}/node_exporter --web.listen-address=":{{ node_exporter_port }}"
Restart=always

[Install]
WantedBy=default.target
""",
    # Nvidia DCGM Exporter for GPU performance
    "ansible/roles/nvidia_dcgm_exporter/defaults/main.yml": r"""nvidia_dcgm_version: "2.4.10"
nvidia_dcgm_download_url: "https://github.com/NVIDIA/DCGMExporter/releases/download/v{{ nvidia_dcgm_version }}/dcgm-exporter-{{ nvidia_dcgm_version }}.linux-amd64.tar.gz"
nvidia_dcgm_install_dir: "/usr/local/bin"
nvidia_dcgm_port: 9400
""",
    "ansible/roles/nvidia_dcgm_exporter/tasks/main.yml": r"""---
- name: Download Nvidia DCGM Exporter
  get_url:
    url: "{{ nvidia_dcgm_download_url }}"
    dest: "/tmp/dcgm-exporter.tar.gz"
    mode: '0644'
  register: download_dcgm

- name: Extract Nvidia DCGM Exporter binary
  unarchive:
    src: "/tmp/dcgm-exporter.tar.gz"
    dest: "/tmp/"
    remote_src: yes
  when: download_dcgm.changed

- name: Move dcgm-exporter binary to install directory
  copy:
    src: "/tmp/dcgm-exporter-{{ nvidia_dcgm_version }}.linux-amd64/dcgm-exporter"
    dest: "{{ nvidia_dcgm_install_dir }}/dcgm-exporter"
    mode: '0755'
  when: download_dcgm.changed

- name: Create systemd service for Nvidia DCGM Exporter
  copy:
    dest: "/etc/systemd/system/dcgm-exporter.service"
    content: |
      [Unit]
      Description=Nvidia DCGM Exporter
      After=network.target

      [Service]
      ExecStart={{ nvidia_dcgm_install_dir }}/dcgm-exporter --web.listen-address=":{{ nvidia_dcgm_port }}"
      Restart=always

      [Install]
      WantedBy=default.target
    mode: '0644'

- name: Reload systemd daemon
  command: systemctl daemon-reload

- name: Enable and start dcgm-exporter service
  systemd:
    name: dcgm-exporter
    enabled: yes
    state: started
""",
    # SLURM Exporter for HPC Queue/Job performance
    "ansible/roles/slurm_exporter/defaults/main.yml": r"""slurm_exporter_version: "0.2.0"
slurm_exporter_download_url: "https://github.com/vpenso/slurm_exporter/releases/download/v{{ slurm_exporter_version }}/slurm_exporter-{{ slurm_exporter_version }}.linux-amd64.tar.gz"
slurm_exporter_install_dir: "/usr/local/bin"
slurm_exporter_port: 9779
""",
    "ansible/roles/slurm_exporter/tasks/main.yml": r"""---
- name: Download Slurm Exporter
  get_url:
    url: "{{ slurm_exporter_download_url }}"
    dest: "/tmp/slurm_exporter.tar.gz"
    mode: '0644'
  register: download_slurm

- name: Extract Slurm Exporter binary
  unarchive:
    src: "/tmp/slurm_exporter.tar.gz"
    dest: "/tmp/"
    remote_src: yes
  when: download_slurm.changed

- name: Move slurm_exporter binary to install directory
  copy:
    src: "/tmp/slurm_exporter-{{ slurm_exporter_version }}.linux-amd64/slurm_exporter"
    dest: "{{ slurm_exporter_install_dir }}/slurm_exporter"
    mode: '0755'
  when: download_slurm.changed

- name: Create systemd service for Slurm Exporter
  copy:
    dest: "/etc/systemd/system/slurm_exporter.service"
    content: |
      [Unit]
      Description=Slurm Prometheus Exporter
      After=network.target

      [Service]
      ExecStart={{ slurm_exporter_install_dir }}/slurm_exporter --web.listen-address=":{{ slurm_exporter_port }}"
      Restart=always

      [Install]
      WantedBy=default.target
    mode: '0644'

- name: Reload systemd daemon
  command: systemctl daemon-reload

- name: Enable and start slurm_exporter service
  systemd:
    name: slurm_exporter
    enabled: yes
    state: started
""",
    # WEKA Exporter for the WEKA environment
    "ansible/roles/wekafs_exporter/defaults/main.yml": r"""wekafs_exporter_version: "1.0.0"
wekafs_exporter_download_url: "https://example.com/wekafs_exporter-{{ wekafs_exporter_version }}.linux-amd64.tar.gz"
wekafs_exporter_install_dir: "/usr/local/bin"
wekafs_exporter_port: 9200
""",
    "ansible/roles/wekafs_exporter/tasks/main.yml": r"""---
- name: Download WEKA Exporter
  get_url:
    url: "{{ wekafs_exporter_download_url }}"
    dest: "/tmp/wekafs_exporter.tar.gz"
    mode: '0644'
  register: download_wekafs

- name: Extract WEKA Exporter binary
  unarchive:
    src: "/tmp/wekafs_exporter.tar.gz"
    dest: "/tmp/"
    remote_src: yes
  when: download_wekafs.changed

- name: Move WEKA Exporter binary to install directory
  copy:
    src: "/tmp/wekafs_exporter-{{ wekafs_exporter_version }}.linux-amd64/wekafs_exporter"
    dest: "{{ wekafs_exporter_install_dir }}/wekafs_exporter"
    mode: '0755'
  when: download_wekafs.changed

- name: Create systemd service for WEKA Exporter
  copy:
    dest: "/etc/systemd/system/wekafs_exporter.service"
    content: |
      [Unit]
      Description=WEKA Environment Prometheus Exporter
      After=network.target

      [Service]
      ExecStart={{ wekafs_exporter_install_dir }}/wekafs_exporter --web.listen-address=":{{ wekafs_exporter_port }}"
      Restart=always

      [Install]
      WantedBy=default.target
    mode: '0644'

- name: Reload systemd daemon
  command: systemctl daemon-reload

- name: Enable and start WEKA Exporter service
  systemd:
    name: wekafs_exporter
    enabled: yes
    state: started
""",
    # Updated Grafana Dashboard JSON (includes panels for Rocky Linux, GPU, SLURM, and WEKA)
    "grafana_dashboards/hpc_dashboard.json": r"""{
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
      "title": "Rocky Linux CPU Usage",
      "type": "graph",
      "targets": [
        { "expr": "100 - (avg by(instance)(irate(node_cpu_seconds_total{mode=\"idle\"}[5m])) * 100)", "legendFormat": "{{instance}}", "refId": "A" }
      ]
    },
    {
      "datasource": "Prometheus",
      "fieldConfig": { "defaults": { "unit": "percent" }, "overrides": [] },
      "gridPos": { "h": 8, "w": 12, "x": 12, "y": 0 },
      "id": 2,
      "title": "Memory Utilization",
      "type": "graph",
      "targets": [
        { "expr": "(1 - (node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes)) * 100", "legendFormat": "{{instance}}", "refId": "B" }
      ]
    },
    {
      "datasource": "Prometheus",
      "fieldConfig": { "defaults": { "unit": "percent" }, "overrides": [] },
      "gridPos": { "h": 8, "w": 12, "x": 0, "y": 8 },
      "id": 3,
      "title": "IO Wait",
      "type": "graph",
      "targets": [
        { "expr": "irate(node_cpu_seconds_total{mode=\"iowait\"}[5m]) * 100", "legendFormat": "{{instance}}", "refId": "C" }
      ]
    },
    {
      "datasource": "Prometheus",
      "fieldConfig": { "defaults": { "unit": "percent" }, "overrides": [] },
      "gridPos": { "h": 8, "w": 12, "x": 12, "y": 8 },
      "id": 4,
      "title": "Storage Utilization",
      "type": "graph",
      "targets": [
        { "expr": "100 - (node_filesystem_free_bytes / node_filesystem_size_bytes * 100)", "legendFormat": "{{mountpoint}}", "refId": "D" }
      ]
    },
    {
      "datasource": "Prometheus",
      "fieldConfig": { "defaults": { "unit": "Bps" }, "overrides": [] },
      "gridPos": { "h": 8, "w": 12, "x": 0, "y": 16 },
      "id": 5,
      "title": "Network Throughput",
      "type": "graph",
      "targets": [
        { "expr": "irate(node_network_receive_bytes_total[5m])", "legendFormat": "{{instance}} recv", "refId": "E" },
        { "expr": "irate(node_network_transmit_bytes_total[5m])", "legendFormat": "{{instance}} xmit", "refId": "F" }
      ]
    },
    {
      "datasource": "Prometheus",
      "fieldConfig": { "defaults": { "unit": "percent" }, "overrides": [] },
      "gridPos": { "h": 8, "w": 12, "x": 12, "y": 16 },
      "id": 6,
      "title": "GPU Utilization",
      "type": "graph",
      "targets": [
        { "expr": "dcgm_gpu_utilization_percent", "legendFormat": "{{gpu}}", "refId": "G" }
      ]
    },
    {
      "datasource": "Prometheus",
      "fieldConfig": { "defaults": { "unit": "none" }, "overrides": [] },
      "gridPos": { "h": 8, "w": 12, "x": 0, "y": 24 },
      "id": 7,
      "title": "SLURM Job Queue Length",
      "type": "graph",
      "targets": [
        { "expr": "slurm_job_queue_length", "legendFormat": "{{cluster}}", "refId": "H" }
      ]
    },
    {
      "datasource": "Prometheus",
      "fieldConfig": { "defaults": { "unit": "none" }, "overrides": [] },
      "gridPos": { "h": 8, "w": 12, "x": 12, "y": 24 },
      "id": 8,
      "title": "WEKA Environment Metrics",
      "type": "graph",
      "targets": [
        { "expr": "weka_metric", "legendFormat": "{{instance}}", "refId": "I" }
      ]
    }
  ],
  "schemaVersion": 30,
  "style": "dark",
  "tags": ["hpc", "rocky", "gpu", "slurm", "weka"],
  "templating": { "list": [] },
  "time": { "from": "now-12h", "to": "now" },
  "timezone": "",
  "title": "HPC Monitoring Dashboard",
  "uid": "hpc-monitoring",
  "version": 1
}"""
}

def create_files():
    for filepath, content in files.items():
        # Ensure parent directory exists
        directory = os.path.dirname(filepath)
        if directory and not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)
        # Write the file
        with open(filepath, "w") as f:
            f.write(content)
        print(f"Created/Updated: {filepath}")

if __name__ == "__main__":
    create_files()
    print("Repository folders and configuration files have been updated.")
