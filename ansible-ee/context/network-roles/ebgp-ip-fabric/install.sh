#!/bin/bash

set -e

ANSIBLEROLES=${ANSIBLEROLES:=/etc/ansible/roles}

mkdir -p ${ANSIBLEROLES}
cp -r roles/* ${ANSIBLEROLES}
