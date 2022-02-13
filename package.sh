#!/bin/sh

TAR_NAME="messiah-ptz-controller.tar.bz2"
INCLUDES="config lib *.py *.sh requirements.txt LICENSE.txt"
EXCLUDES="--exclude=**/__pycache__"
OPTIONS="--dereference --hard-dereference"

echo "Packaging the project to ${TAR_NAME}"
tar -cjpf ${TAR_NAME} ${EXCLUDES} ${OPTIONS} --transform='flags=r;s|^|messiah-ptz-controller/|' ${INCLUDES}
