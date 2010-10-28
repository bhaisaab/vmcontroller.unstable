#!/bin/sh

echo "Make sure you have buildout script in ../buildout/bin/"
buildout=$PWD/../buildout/bin/buildout
echo "using buildout: $buildout"
$buildout setup ../src/vmcontroller.common/setup.py bdist_egg -d $PWD/../dist
$buildout setup ../src/vmcontroller.host/setup.py bdist_egg -d $PWD/../dist
$buildout setup ../src/vmcontroller.vm/setup.py bdist_egg -d $PWD/../dist
echo "Eggs created in dist folder: $PWD/../dist"
