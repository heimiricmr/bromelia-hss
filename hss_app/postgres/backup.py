# -*- coding: utf-8 -*-
"""
    postgres.backup
    ~~~~~~~~~~~~~~~

    This module implements a tool to backup Bromelia-HSS's database data.

    :copyright: (c) 2021-present Henrique Marques Ribeiro.
    :license: MIT, see LICENSE for more details.
"""

import datetime
import os
import re
import subprocess
import sys

base_dir = os.path.dirname(os.path.abspath(__file__))
backup_dir = os.path.join(base_dir, "backup")


def execute_docker_container_ls():
    try:
        process = subprocess.Popen(
            ["docker", "container", "ls"], 
            stdout=subprocess.PIPE
        )
        output = process.communicate()[0]
        return output.decode("utf-8")

    except FileNotFoundError:
        print(f"[error] command not found: docker")


def get_container_id(docker_output):
    pattern = re.findall(r"([a-z0-9]{12})\s*hss_app-postgres", docker_output)
    if pattern:
        return pattern[0]

    print(f"[error] container not found: hss_app-postgres")


def dump(container_id):
    if not os.path.exists(backup_dir):
        os.mkdir(backup_dir)

    now = datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
    backup_filepath = os.path.join(backup_dir, f"{now}-backup.sql")

    with open(backup_filepath, "w") as outfile:
        subprocess.run(
            ["docker", "exec", "-it", container_id, "pg_dumpall", "-U", "postgres"], 
            stdout=outfile
        )


def main():
    #: Check if Bromelia-HSS is running as docker service
    docker_output = execute_docker_container_ls()
    if docker_output is None:
        sys.exit(0)

    #: Get PostgreSQL container id
    container_id = get_container_id(docker_output)
    if container_id is None:
        sys.exit(0)

    #: Generate backup .sql file
    dump(container_id)


if __name__ == "__main__":
    main()