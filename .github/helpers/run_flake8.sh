#!/bin/sh
flake8 --ignore E261,E501,W291,W293 $1 > $2
exit 0