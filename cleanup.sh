#!/bin/bash

# Variables for log colors
YELLOW="\033[0;33m"
GREEN="\033[0;32m"
NC="\033[0m"

cleanUpBromeliaHss() {
    echo -e "${GREEN}$(date +%d/%m/%Y) - $(date +%T) - Clean Up Bromélia HSS ${NC}"
    echo

    #: Cleaning up hss_app containers
    if [[ $(docker container ls -a | grep hss_app | wc -l) -gt 0 ]]; then
        echo "Cleaning up hss_app containers"
        docker container stop $(docker container ls -a | grep hss_app | awk '{print $1}')
        docker container rm -f $(docker container ls -a | grep hss_app | awk '{print $1}')
    else
        echo "There is no hss_app containers to clean up"
    fi

    #: Cleaning up hss_app images
    if [[ $(docker image ls | grep hss_app | wc -l) -gt 0 ]]; then
        echo "Cleaning up hss_app images"
        docker image rm -f $(docker image ls | grep hss_app | awk '{print $3}')
    else
        echo "There is no hss_app images to clean up"
    fi

    #: Cleaning up hss_app networks
    if [[ $(docker network ls | grep hss_app | wc -l) -gt 0 ]]; then
        echo "Cleaning up hss_app networks"
        docker network rm $(docker network ls | grep hss_app | awk '{print $1}')
    else
        echo "There is no hss_app networks to clean up"
    fi

    echo
}

cleanUpZabbix() {
    echo -e "${GREEN}$(date +%d/%m/%Y) - $(date +%T) - Clean Up Zabbix ${NC}"
    echo

    #: Cleaning up zabbix containers
    if [[ $(docker container ls -a | grep zabbix | wc -l) -gt 0 ]]; then
        echo "Cleaning up zabbix containers"
        docker container stop $(docker container ls -a | grep zabbix-docker | awk '{print $1}')
        docker container rm -f $(docker container ls -a | grep zabbix-docker | awk '{print $1}')
    else
        echo "There is no zabbix containers to clean up"
    fi

    #: Cleaning up zabbix images
    if [[ $(docker image ls | grep zabbix | wc -l) -gt 0 ]]; then
        echo "Cleaning up zabbix images"
        docker image rm -f $(docker image ls | grep zabbix | awk '{print $3}')
    else
        echo "There is no zabbix images to clean up"
    fi

    #: Cleaning up zabbix networks
    if [[ $(docker network ls | grep zbx_net | wc -l) -gt 0 ]]; then
        echo "Cleaning up zabbix networks - "
        docker network rm $(docker network ls | grep zbx_net | awk '{print $1}')
    else
        echo "There is no zabbix networks to clean up"
    fi

    if [[ $(docker network ls | grep zabbix | wc -l) -gt 0 ]]; then
        echo "Cleaning up zabbix networks: zabbix-docker_default"
        docker network rm $(docker network ls | grep zabbix | awk '{print $1}')
    else
        echo "There is no zabbix networks to clean up"
    fi

    echo
}

main() {
    cleanUpBromeliaHss
    cleanUpZabbix
}

main