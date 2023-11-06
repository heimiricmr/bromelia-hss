#!/bin/bash

# Variables for log colors
YELLOW="\033[0;33m"
GREEN="\033[0;32m"
NC="\033[0m"

stopBromeliaHss() {
    echo -e "${GREEN}$(date +%d/%m/%Y) - $(date +%T) - Stop Bromélia HSS ${NC}"
    echo

    #: Stopping hss_app containers
    if [[ $(docker container ls -a | grep hss_app | wc -l) -gt 0 ]]; then
        echo "Stopping hss_app containers"
        docker container stop $(docker container ls -a | grep hss_app | awk '{print $1}')
    else
        echo "There is no hss_app containers to stop"
    fi

    echo
}

stopZabbix() {
    echo -e "${GREEN}$(date +%d/%m/%Y) - $(date +%T) - Stop Zabbix ${NC}"
    echo

    #: Stopping zabbix containers
    if [[ $(docker container ls -a | grep zabbix | wc -l) -gt 0 ]]; then
        echo "Stopping zabbix containers"
        docker container stop $(docker container ls -a | grep zabbix-docker | awk '{print $1}')
    else
        echo "There is no zabbix containers to stop"
    fi

    echo
}

main() {
    stopBromeliaHss
    stopZabbix
}

main