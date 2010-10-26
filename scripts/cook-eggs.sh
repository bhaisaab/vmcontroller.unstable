#!/bin/sh

buildout setup ../src/vmcontroller.common/setup.py bdist_egg -d $PWD/../dist
buildout setup ../src/vmcontroller.host/setup.py bdist_egg -d $PWD/../dist
buildout setup ../src/vmcontroller.vm/setup.py bdist_egg -d $PWD/../dist
echo "Eggs created in dist folder"
