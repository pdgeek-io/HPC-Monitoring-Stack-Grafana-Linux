import os

# Dictionary mapping file paths to their content.
files = {
    # Updated inventory with a new [grafana] group
    "ansible/inventory": r"""[hpc1]
rocky1.example.com
rocky2.example.com

[hpc2]
rocky3.example.com
rocky4.example.com

[grafana]
grafana.example.com

[job_scheduler]
scheduler.example.com

[storage_weka]
weka1.example.com

[gpu_nodes]
gpu1.example.com
""",
    # Docker Compose file to deploy Grafana (and Prometheus)
    "docker/grafana-stack/docker-compose.yml": r"""version: '3.8'
services:
  grafana:
    image: grafana/grafana:latest
    container_name: grafana
    ports:
      - "3000:3000"
    volumes:
      - grafana_data:/var/lib/grafana
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
  prometheus:
    image: prom/prometheus:latest
    container_name: prometheus
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
volumes:
  grafana_data:
""",
    # Ansible role defaults for the Grafana stack deployment
    "ansible/roles/grafana_stack/defaults/main.yml": r"""# Default variables for Grafana Stack deployment
grafana_stack_compose_file: "{{ playbook_dir }}/../../docker/grafana-stack/docker-compose.yml"
grafana_stack_project_name: "grafana_stack"
""",
    # Ansible role tasks for the Grafana stack deployment (using docker_compose module)
    "ansible/roles/grafana_stack/tasks/main.yml": r"""---
- name: Deploy Grafana Stack using Docker Compose
  docker_compose:
    project_src: "{{ grafana_stack_compose_file | dirname }}"
    files:
      - "{{ grafana_stack_compose_file | basename }}"
    restarted: yes
    project_name: "{{ grafana_stack_project_name }}"
""",
    # Ansible playbook to deploy the Grafana stack on hosts in the [grafana] group
    "ansible/playbooks/grafana_stack.yml": r"""---
- name: Deploy Grafana Stack via Docker Compose
  hosts: grafana
  become: yes
  roles:
    - grafana_stack
"""
}

def create_files():
    for filepath, content in files.items():
        # Ensure parent directory exists.
        directory = os.path.dirname(filepath)
        if directory and not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)
        # Write content to the file.
        with open(filepath, "w") as f:
            f.write(content)
        print(f"Created/Updated: {filepath}")

if __name__ == "__main__":
    create_files()
    print("Repository updated with Grafana stack deployment files.")
