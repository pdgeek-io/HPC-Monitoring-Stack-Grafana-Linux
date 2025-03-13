import os
import shutil

# Mapping of file paths (excluding README.md) to their content.
files = {
    "ansible/inventory": r"""[compute_nodes]
compute1.example.com
compute2.example.com

[gpu_nodes]
gpu1.example.com

[job_scheduler]
scheduler.example.com

[storage_weka]
weka1.example.com

[object_storage_dell]
dell1.example.com

[network_infiniband]
ib1.example.com

[network_juniper]
juniper1.example.com

[filesystem_rocky]
fs1.example.com

[application_profiling]
app1.example.com
""",
    "ansible/playbooks/hpc_monitoring.yml": r"""---
- name: Configure Compute Nodes with Node Exporter
  hosts: compute_nodes
  become: yes
  roles:
    - node_exporter

- name: Configure GPU Nodes with Nvidia DCGM Exporter
  hosts: gpu_nodes
  become: yes
  roles:
    - nvidia_dcgm_exporter

- name: Configure Job Scheduler with Slurm Exporter
  hosts: job_scheduler
  become: yes
  roles:
    - slurm_exporter

- name: Configure WekaFS Storage with WekaFS Exporter
  hosts: storage_weka
  become: yes
  roles:
    - wekafs_exporter

- name: Configure Dell ECS Object Storage Exporter
  hosts: object_storage_dell
  become: yes
  roles:
    - dell_ecs_exporter

- name: Configure Infiniband Networking Exporters (SNMP and UFM)
  hosts: network_infiniband
  become: yes
  roles:
    - snmp_exporter
    - ufm_exporter

- name: Configure Juniper Networking with SNMP Exporter
  hosts: network_juniper
  become: yes
  roles:
    - snmp_exporter

- name: Configure Filesystem Performance on Rocky Linux with Node Exporter
  hosts: filesystem_rocky
  become: yes
  roles:
    - node_exporter

- name: Configure Application Profiling Exporters (VTune and Nsight)
  hosts: application_profiling
  become: yes
  roles:
    - vtune_exporter
    - nsight_exporter
""",
    "ansible/roles/node_exporter/defaults/main.yml": r"""node_exporter_version: "1.5.0"
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
Description=Prometheus Node Exporter
After=network.target

[Service]
User={{ node_exporter_user }}
ExecStart={{ node_exporter_install_dir }}/node_exporter --web.listen-address=":{{ node_exporter_port }}"
Restart=always

[Install]
WantedBy=default.target
""",
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
    "ansible/roles/wekafs_exporter/defaults/main.yml": r"""wekafs_exporter_version: "1.0.0"
wekafs_exporter_download_url: "https://example.com/wekafs_exporter-{{ wekafs_exporter_version }}.linux-amd64.tar.gz"
wekafs_exporter_install_dir: "/usr/local/bin"
wekafs_exporter_port: 9200
""",
    "ansible/roles/wekafs_exporter/tasks/main.yml": r"""---
- name: Download WekaFS Exporter
  get_url:
    url: "{{ wekafs_exporter_download_url }}"
    dest: "/tmp/wekafs_exporter.tar.gz"
    mode: '0644'
  register: download_wekafs

- name: Extract WekaFS Exporter binary
  unarchive:
    src: "/tmp/wekafs_exporter.tar.gz"
    dest: "/tmp/"
    remote_src: yes
  when: download_wekafs.changed

- name: Move WekaFS Exporter binary to install directory
  copy:
    src: "/tmp/wekafs_exporter-{{ wekafs_exporter_version }}.linux-amd64/wekafs_exporter"
    dest: "{{ wekafs_exporter_install_dir }}/wekafs_exporter"
    mode: '0755'
  when: download_wekafs.changed

- name: Create systemd service for WekaFS Exporter
  copy:
    dest: "/etc/systemd/system/wekafs_exporter.service"
    content: |
      [Unit]
      Description=WekaFS Prometheus Exporter
      After=network.target

      [Service]
      ExecStart={{ wekafs_exporter_install_dir }}/wekafs_exporter --web.listen-address=":{{ wekafs_exporter_port }}"
      Restart=always

      [Install]
      WantedBy=default.target
    mode: '0644'

- name: Reload systemd daemon
  command: systemctl daemon-reload

- name: Enable and start wekafs_exporter service
  systemd:
    name: wekafs_exporter
    enabled: yes
    state: started
""",
    "ansible/roles/dell_ecs_exporter/defaults/main.yml": r"""dell_ecs_exporter_version: "1.0.0"
dell_ecs_exporter_download_url: "https://example.com/dell_ecs_exporter-{{ dell_ecs_exporter_version }}.linux-amd64.tar.gz"
dell_ecs_exporter_install_dir: "/usr/local/bin"
dell_ecs_exporter_port: 9300
""",
    "ansible/roles/dell_ecs_exporter/tasks/main.yml": r"""---
- name: Download Dell ECS Exporter
  get_url:
    url: "{{ dell_ecs_exporter_download_url }}"
    dest: "/tmp/dell_ecs_exporter.tar.gz"
    mode: '0644'
  register: download_dell_ecs

- name: Extract Dell ECS Exporter binary
  unarchive:
    src: "/tmp/dell_ecs_exporter.tar.gz"
    dest: "/tmp/"
    remote_src: yes
  when: download_dell_ecs.changed

- name: Move Dell ECS Exporter binary to install directory
  copy:
    src: "/tmp/dell_ecs_exporter-{{ dell_ecs_exporter_version }}.linux-amd64/dell_ecs_exporter"
    dest: "{{ dell_ecs_exporter_install_dir }}/dell_ecs_exporter"
    mode: '0755'
  when: download_dell_ecs.changed

- name: Create systemd service for Dell ECS Exporter
  copy:
    dest: "/etc/systemd/system/dell_ecs_exporter.service"
    content: |
      [Unit]
      Description=Dell ECS Prometheus Exporter
      After=network.target

      [Service]
      ExecStart={{ dell_ecs_exporter_install_dir }}/dell_ecs_exporter --web.listen-address=":{{ dell_ecs_exporter_port }}"
      Restart=always

      [Install]
      WantedBy=default.target
    mode: '0644'

- name: Reload systemd daemon
  command: systemctl daemon-reload

- name: Enable and start dell_ecs_exporter service
  systemd:
    name: dell_ecs_exporter
    enabled: yes
    state: started
""",
    "ansible/roles/snmp_exporter/defaults/main.yml": r"""snmp_exporter_version: "0.20.0"
snmp_exporter_download_url: "https://github.com/prometheus/snmp_exporter/releases/download/v{{ snmp_exporter_version }}/snmp_exporter-{{ snmp_exporter_version }}.linux-amd64.tar.gz"
snmp_exporter_install_dir: "/usr/local/bin"
snmp_exporter_port: 9116
snmp_exporter_config: "/etc/snmp_exporter/snmp.yml"
""",
    "ansible/roles/snmp_exporter/tasks/main.yml": r"""---
- name: Download SNMP Exporter
  get_url:
    url: "{{ snmp_exporter_download_url }}"
    dest: "/tmp/snmp_exporter.tar.gz"
    mode: '0644'
  register: download_snmp

- name: Extract SNMP Exporter binary
  unarchive:
    src: "/tmp/snmp_exporter.tar.gz"
    dest: "/tmp/"
    remote_src: yes
  when: download_snmp.changed

- name: Move SNMP Exporter binary to install directory
  copy:
    src: "/tmp/snmp_exporter-{{ snmp_exporter_version }}.linux-amd64/snmp_exporter"
    dest: "{{ snmp_exporter_install_dir }}/snmp_exporter"
    mode: '0755'
  when: download_snmp.changed

- name: Deploy SNMP Exporter configuration file
  copy:
    dest: "{{ snmp_exporter_config }}"
    content: |
      # SNMP Exporter configuration
      modules:
        default:
          walk:
            - 1.3.6.1.2.1.1
            - 1.3.6.1.2.1.2
          version: 2c
    mode: '0644'

- name: Create systemd service for SNMP Exporter
  copy:
    dest: "/etc/systemd/system/snmp_exporter.service"
    content: |
      [Unit]
      Description=Prometheus SNMP Exporter
      After=network.target

      [Service]
      ExecStart={{ snmp_exporter_install_dir }}/snmp_exporter --config.file={{ snmp_exporter_config }} --web.listen-address=":{{ snmp_exporter_port }}"
      Restart=always

      [Install]
      WantedBy=default.target
    mode: '0644'

- name: Reload systemd daemon
  command: systemctl daemon-reload

- name: Enable and start snmp_exporter service
  systemd:
    name: snmp_exporter
    enabled: yes
    state: started
""",
    "ansible/roles/ufm_exporter/defaults/main.yml": r"""ufm_exporter_version: "1.0.0"
ufm_exporter_download_url: "https://example.com/ufm_exporter-{{ ufm_exporter_version }}.linux-amd64.tar.gz"
ufm_exporter_install_dir: "/usr/local/bin"
ufm_exporter_port: 9201
""",
    "ansible/roles/ufm_exporter/tasks/main.yml": r"""---
- name: Download UFM Exporter
  get_url:
    url: "{{ ufm_exporter_download_url }}"
    dest: "/tmp/ufm_exporter.tar.gz"
    mode: '0644'
  register: download_ufm

- name: Extract UFM Exporter binary
  unarchive:
    src: "/tmp/ufm_exporter.tar.gz"
    dest: "/tmp/"
    remote_src: yes
  when: download_ufm.changed

- name: Move UFM Exporter binary to install directory
  copy:
    src: "/tmp/ufm_exporter-{{ ufm_exporter_version }}.linux-amd64/ufm_exporter"
    dest: "{{ ufm_exporter_install_dir }}/ufm_exporter"
    mode: '0755'
  when: download_ufm.changed

- name: Create systemd service for UFM Exporter
  copy:
    dest: "/etc/systemd/system/ufm_exporter.service"
    content: |
      [Unit]
      Description=Mellanox UFM Exporter
      After=network.target

      [Service]
      ExecStart={{ ufm_exporter_install_dir }}/ufm_exporter --web.listen-address=":{{ ufm_exporter_port }}"
      Restart=always

      [Install]
      WantedBy=default.target
    mode: '0644'

- name: Reload systemd daemon
  command: systemctl daemon-reload

- name: Enable and start ufm_exporter service
  systemd:
    name: ufm_exporter
    enabled: yes
    state: started
""",
    "ansible/roles/vtune_exporter/defaults/main.yml": r"""# VTune integration typically involves log export rather than a running binary.
vtune_exporter_log_dir: "/var/log/vtune"
""",
    "ansible/roles/vtune_exporter/tasks/main.yml": r"""---
- name: Ensure VTune log directory exists
  file:
    path: "{{ vtune_exporter_log_dir }}"
    state: directory
    owner: root
    group: root
    mode: '0755'

# Additional tasks to parse and expose VTune logs can be added here.
""",
    "ansible/roles/nsight_exporter/defaults/main.yml": r"""# Nsight integration similarly may involve log parsing.
nsight_exporter_log_dir: "/var/log/nsight"
""",
    "ansible/roles/nsight_exporter/tasks/main.yml": r"""---
- name: Ensure Nsight log directory exists
  file:
    path: "{{ nsight_exporter_log_dir }}"
    state: directory
    owner: root
    group: root
    mode: '0755'

# Additional tasks to parse and expose Nsight logs can be added here.
""",
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
      "fieldConfig": {
        "defaults": {
          "unit": "percent"
        },
        "overrides": []
      },
      "gridPos": {
        "h": 9,
        "w": 12,
        "x": 0,
        "y": 0
      },
      "id": 1,
      "title": "Compute Node CPU Usage",
      "type": "graph",
      "targets": [
        {
          "expr": "100 - (avg by (instance) (irate(node_cpu_seconds_total{mode=\"idle\"}[5m])) * 100)",
          "interval": "",
          "legendFormat": "{{instance}}",
          "refId": "A"
        }
      ]
    },
    {
      "datasource": "Prometheus",
      "gridPos": {
        "h": 9,
        "w": 12,
        "x": 12,
        "y": 0
      },
      "id": 2,
      "title": "GPU Utilization",
      "type": "graph",
      "targets": [
        {
          "expr": "dcgm_gpu_utilization_percent",
          "interval": "",
          "legendFormat": "{{gpu}}",
          "refId": "B"
        }
      ]
    }
  ],
  "schemaVersion": 30,
  "style": "dark",
  "tags": [
    "hpc",
    "monitoring"
  ],
  "templating": {
    "list": []
  },
  "time": {
    "from": "now-6h",
    "to": "now"
  },
  "timepicker": {},
  "timezone": "",
  "title": "HPC Monitoring Dashboard",
  "uid": "hpc-monitoring",
  "version": 1
}"""
}

def create_files():
    for filepath, content in files.items():
        # If a conflicting directory exists where a file should be created, remove it.
        if os.path.exists(filepath) and os.path.isdir(filepath):
            print(f"Removing conflicting directory: {filepath}")
            shutil.rmtree(filepath)
        # Ensure the parent directory exists
        directory = os.path.dirname(filepath)
        if directory and not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)
        # Write the file
        with open(filepath, "w") as f:
            f.write(content)
        print(f"Created: {filepath}")

if __name__ == "__main__":
    create_files()
    print("Repository structure and configuration files (excluding README) have been created.")
