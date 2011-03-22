cd ../src

cd vmcontroller.common
echo vmcontroller.common: `python setup.py --version`
cd ..

cd vmcontroller.host
echo vmcontroller.host: `python setup.py --version`
cd ..

cd vmcontroller.guest
echo vmcontroller.vm: `python setup.py --version`
cd ..
