import setuptools, os
with open(os.path.join(os.path.dirname(__file__), 'README.rst')) as doc:
    __doc__=doc.read()

setuptools.setup(
    name='teacup',
    version='0.9',
    url='https://github.com/benwbooth/python-teacup',
    author='Ben Booth',
    author_email='benwbooth@gmail.com',
    license='MIT',
    keywords="python module html markdown teacup coffeecup coffeekup templating template library",
    zip_safe=True,
    description="HTML Templating DSL for Python",
    py_modules=['teacup'],
    install_requires=['beautifulsoup4','mistune'])
