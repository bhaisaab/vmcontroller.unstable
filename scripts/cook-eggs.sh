#!/bin/sh

buildout=$PWD/../bin/buildout

if [ ! -f $buildout ]; then
  echo "BuildOut not created in $buildout... please run the build script...";
  exit
fi

echo "Using BuildOut: $buildout"
mkdir -p ../dist
$buildout setup ../src/vmcontroller.common/setup.py bdist_egg -d $PWD/../dist
$buildout setup ../src/vmcontroller.host/setup.py bdist_egg -d $PWD/../dist
$buildout setup ../src/vmcontroller.guest/setup.py bdist_egg -d $PWD/../dist
echo "Eggs created in dist folder: $PWD/../dist"
