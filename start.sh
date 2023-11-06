#!/bin/bash

# Variables for log colors
YELLOW="\033[0;33m"
GREEN="\033[0;32m"
NC="\033[0m"

startBromeliaHss() {
    echo -e "${GREEN}$(date +%d/%m/%Y) - $(date +%T) - Start Bromélia HSS ${NC}"
    echo

    #: Starting hss_app containers
    if [[ $(docker container ls -a | grep hss_app | wc -l) -gt 0 ]]; then
        echo "Starting hss_app containers"
        docker container start $(docker container ls -a | grep hss_app | awk '{print $1}')
    else
        echo "There is no hss_app containers to start"
    fi

    echo
}

startZabbix() {
    echo -e "${GREEN}$(date +%d/%m/%Y) - $(date +%T) - Start Zabbix ${NC}"
    echo

    #: Starting zabbix containers
    if [[ $(docker container ls -a | grep zabbix | wc -l) -gt 0 ]]; then
        echo "Starting zabbix containers"
        docker container start $(docker container ls -a | grep zabbix-docker | awk '{print $1}')
    else
        echo "There is no zabbix containers to start"
    fi

    echo
}

main() {
    startBromeliaHss
    startZabbix
}

main