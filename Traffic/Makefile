VERSION:=$(shell python3 setup.py --version)

install:
	sudo python3 setup.py install

uninstall:
	sudo pip uninstall cicflowmeter -y

clean:
	sudo rm -rf ./src/*.egg-info build dist
