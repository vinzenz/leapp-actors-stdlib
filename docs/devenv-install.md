# Installing the actor development environment

This demo encourages to use virtualenv to setup the actor development environment.

First step to do so, is to create a new virtualenv called tut and activate it
```shell
	$ cd ~/devel
	$ virtualenv -p /usr/bin/python2.7 tut
	$ . tut/bin/activate
```

Next we will install the framework via pip
```shell
	$ pip install git+https://github.com/leapp-to/leapp-actors-stdlib
```

Once the framework is install in your virtualenv environment you can start using the snactor tool.
```shell
	$ snactor -h
```

## A screen cast of the steps above
![Installation Tutorial Cast](install.gif)
