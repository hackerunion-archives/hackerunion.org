Hacker Union
=====

This is the code that powers [hackerunion.org](http://www.hackerunion.org). It is built on top of [petri](https://github.com/huffpostlabs/petri), an open source project developed at HuffPost Labs. The backend uses the python django framework, and the front end is built using the Zurb Foundation framework.

Dependencies
----

* Scss / sass - Install sass, ```gem install sass```
* pip
* virtualenv - ```pip install virtualenv```
* mysql - only used on production, but you need it to install the ```python-mysql``` dependency. To install on osx do a ```brew install mysql``` To install on Ubuntu apt-get install libmysqlclient-dev
* sqlite - the database used locally. probably is already installed


Setting up the Database
----

```DJANGO_LOCAL=True ./manage.py syncdb --noinput``` (no need to create a superuser, one will be created for you. see the <a href="#test-users">Test User</a> section.).


Running Locally
----

1. Create a virtualenv in your git directory (don't worry, it will be ignored on checkins) -- ```virtualenv env```
2. Install all the requirements (ensure ```env``` is active by running "env/bin/activate") -- ```pip install -r var/etc/requirements.txt```
3. [optional] Run the celery tasks: ```DJANGO_LOCAL=True ./manage.py celeryd -v 2 -B -E -l INFO``` (this should run in a separate terminal from the server)
4. Run the server in local mode -- ```var/bin/runlocal.bash``` or ```DJANGO_LOCAL=True python manage.py runserver```
5. Visit <http://localhost:8000/>


### Custom CSS Watching

If you want to enable the dynamic chapter specific CSS updating, you need to use [compass](http://compass-style.org/) with [bundler](http://gembundler.com/). Once that is installed, the following command will watch and keep styles updated:

```
cd hackerunion.org/static
bundle install # only need to do this once

bundle exec compass watch
```

Style changes should be made to the file ```static/sass/_app.scss```.


Test Users
----

We automatically create a test user with superuser abilities. 

* Username: ```admin```
* password: ```testuser```


Contributing
---

All pull requests are welcome, no matter the size. For push access make a few awesome pull requests, or contact one of
the maintainers listed below.

###Maintainers

* [Brandon Diamond](http://www.twitter.com/brandondiamond)
* [Ben Beecher](http://www.github.com/gone)


###Structure

Currently, all development occurs via the *hackerunion/website* fork of the *huffpostlabs/petri* project. Both of these projects
are open source under the GPL.

This is temporary! We're working this way as Petri is currently coupled to the Hacker Union use case.

Once we've isolated the two, we'll properly divide efforts: Hacker Union-specific updates will go here, and system-wide
updates will go to Petri.

This seemed to make the most sense as Hacker Union is an instance of Petri (much like any organization's deployment of
Petri ought to be -- though we hope to have a non-source configuration mechanism down the road).

License
----

This project is licensed under GNU GENERAL PUBLIC LICENSE VERSION 3. See the file [LICENSE.md](LICENSE.md) for a copy of the license.
