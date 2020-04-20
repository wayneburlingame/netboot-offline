#!/bin/bash

# This is an example of all-in-one server: DHCP, TFTP server, HTTP server for PXE and storage
# It requires root privileges (launch with sudo) to launch dnsmasq
# It requires also python3

PXE_PORT=80
STORAGE_PORT=8080

if [ $UID -ne 0 ]; then
    echo "Please run this script as root"
    exit 1
fi

python3 -m http.server --directory ../netboot.xyz/buildout/ ${PXE_PORT} &
PXE_PID=$!

python3 -m http.server --directory out/ ${STORAGE_PORT} &
STORAGE_PID=$!

in.tftpd -L -s -vv ../netboot.xyz/buildout/ipxe/ &
TFTP_PID=$!

# TODO: dnsmasq

function cleanup() {
    echo "Stopping services"
    kill $PXE_PID $STORAGE_PID $TFTP_PID
}

trap cleanup EXIT

echo "All services started, press enter to terminate"
read TMP
