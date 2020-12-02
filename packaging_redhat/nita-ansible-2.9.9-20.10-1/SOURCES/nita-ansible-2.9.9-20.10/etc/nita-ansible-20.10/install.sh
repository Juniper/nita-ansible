#!/bin/bash

# ********************************************************
#
# Project: nita-ansible
# Version: 20.10
#
# Copyright (c) Juniper Networks, Inc., 2020. All rights reserved.
#
# Notice and Disclaimer: This code is licensed to you under the Apache 2.0 License (the "License"). You may not use this code except in compliance with the License. This code is not an official Juniper product. You can obtain a copy of the License at https://www.apache.org/licenses/LICENSE-2.0.html
#
# SPDX-License-Identifier: Apache-2.0
#
# Third-Party Code: This code may depend on other components under separate copyright notice and license terms. Your use of the source code for those components is subject to the terms and conditions of the respective license as noted in the Third-Party source code file.
#
# ********************************************************

PACKAGE=nita-ansible-2.9.9
VERSION=20.10-1
IMAGES_DIR=/usr/share/${PACKAGE}/images

# stop the script if a command fails
set -e

# function to add docker images
function add_image {

    SRC="$1"
    TAG="$2"

    echo "Adding docker image $2"

    # load the image
    RESPONSE=`docker load -q < ${SRC}`
    echo $RESPONSE
    ID=`echo ${RESPONSE} | awk -F: '{ print \$3 }'`

    if [[ "x$ID" == "x" ]]; then
        echo "Failed to load image $SRC"
        exit 1
    fi

    # tag the image if it isn't already tagged in the tar.gz file
    # older versions of docker-ce have this issue
    if [[ `docker images | awk '{print $1":"$2}' | grep -c "$TAG"` == 0 ]]; then
        docker tag "$ID" "$TAG"
    fi

    docker tag "$TAG" "${TAG%:*}:_nita_release_$VERSION"

}

# load docker images
add_image $IMAGES_DIR/nita-ansible-${VERSION}.tar.gz juniper/nita-ansible:20.10-1