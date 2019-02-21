# -*- encoding: utf-8 -*-
# ! python3

import shutil

from invoke import run, task


@task
def clean_build():
    shutil.rmtree('x_django_app_maker.egg-info', ignore_errors=True)
    shutil.rmtree('build', ignore_errors=True)
    shutil.rmtree('dist', ignore_errors=True)
    shutil.rmtree('__pycache__', ignore_errors=True)


@task
def lint():
    run("flake8 x_django_app_maker tests")


@task
def test():
    run("py.test --verbose --showlocals tests/")


@task
def test_all():
    run("tox")


@task
def test_cov():
    run("py.test --verbose --showlocals --cov=x_django_app_maker tests/")


@task
def test_setuptools():
    run("python setup.py test")


@task
def test_nosetests():
    run("python setup.py nosetests -v --with-doctest")


@task
def coverage():
    run("coverage run --source x_django_app_maker setup.py test")
    run("coverage report -m")
    run("coverage html")


@task
def install_requirements():
    run("pip install -r requirements.txt --upgrade --use-wheel")


@task
def test_install():
    run("pip uninstall x_django_app_maker --yes", warn=True)

    run("pip install --use-wheel --no-index --find-links dist x_django_app_maker")
    run("pip uninstall x_django_app_maker --yes")


@task
def build():
    run("python setup.py check --verbose --strict --restructuredtext")

    run("python setup.py build")
    run("python setup.py sdist")
    run("python setup.py bdist_wheel")


@task
def publish():
    run('python setup.py sdist upload -r pypi')
    run('python setup.py bdist_wheel upload -r pypi')
