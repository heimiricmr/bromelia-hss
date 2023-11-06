#!/bin/bash

# Variables for log colors
YELLOW="\033[0;33m"
GREEN="\033[0;32m"
NC="\033[0m"

cloneZabbix() {
    echo -e "${GREEN}$(date +%d/%m/%Y) - $(date +%T) - Clone Zabbix repo ${NC}"
    echo

    cd zabbix
    [ ! -d "./zabbix-docker" ] && git clone https://github.com/zabbix/zabbix-docker
    cd ..
}

buildAndRunZabbix() {
    echo -e "${GREEN}$(date +%d/%m/%Y) - $(date +%T) - Build & Run Zabbix ${NC}"
    echo

    cd zabbix/zabbix-docker
    docker-compose -f docker-compose_v3_alpine_pgsql_latest.yaml up -d --build
    cd ../..
}

buildAndRunBromeliaHss() {
    echo -e "${GREEN}$(date +%d/%m/%Y) - $(date +%T) - Build & Run Bromélia HSS ${NC}"
    echo

    cd hss_app
    docker-compose -f docker-compose.yaml up -d --build
    cd ..
}

buildAndRunBromeliaHssWithZabbix() {
    echo -e "${GREEN}$(date +%d/%m/%Y) - $(date +%T) - Build & Run Bromélia HSS with Zabbix${NC}"
    echo

    cd hss_app
    docker-compose -f docker-compose.zabbix.yaml up -d --build
    cd ..
}

includeZabbixInstallation() {
    echo -e "${YELLOW}$(date +%d/%m/%Y) - $(date +%T) - Start Bromélia HSS installation ${NC}"
    echo

    cloneZabbix
    buildAndRunZabbix
    buildAndRunBromeliaHssWithZabbix

    echo -e "${YELLOW}$(date +%d/%m/%Y) - $(date +%T) - End Bromélia HSS installation ${NC}"
    exit 1
}

defaultInstallation() {
    echo -e "${YELLOW}$(date +%d/%m/%Y) - $(date +%T) - Start Bromélia HSS installation ${NC}"
    echo

    buildAndRunBromeliaHss

    echo -e "${YELLOW}$(date +%d/%m/%Y) - $(date +%T) - End Bromélia HSS installation ${NC}"
    exit 1
}

main() {
    echo $1
    #: Bromélia installation with Zabbix
    if [[ "$1" == "include-zabbix" ]]; then
        includeZabbixInstallation
    fi
    
    #: Default installation
    if [[ "$1" == "default" ]]; then
        defaultInstallation
    fi

    defaultInstallation
}

main "$1"