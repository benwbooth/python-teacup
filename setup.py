"""
HTML Templating DSL for Python.

A simple HTML templating library that uses a DSL
mini-language. I tried to design it to be similar in feel
to Teacup/CoffeeKup (https://github.com/goodeggs/teacup). I
also took inspiration from jamescasbon's template.py script
(https://gist.github.com/jamescasbon/1461441).

Also includes the md() function for embedding markdown, and an option
for outputting prettified HTML.

Example usage::

    from teacup import *

    with html:
        with head:
            pass
        with body:
            with p:
                md("This is a **test!**")
            with p({"class":"test"}, id="testme"):
                text("Another test")
                a("Click here", href="https://google.com")

    print(render())

The python "with" keyword is used to nest HTML tags.

"""

from setuptools import setup

setup(
    name='teacup',
    version='0.3',
    url='https://github.com/benwbooth/python-teacup',
    author='Ben Booth',
    author_email='benwbooth@gmail.com',
    license='MIT',
    keywords="python module html markdown teacup coffeecup coffeekup templating template library",
    zip_safe=True,
    description="HTML Templating DSL for Python",
    packages=['teacup'])
