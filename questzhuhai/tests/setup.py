import sys
try:
    import ez_setup
    ez_setup.use_setuptools()
except ImportError:
    pass
from setuptools import setup
setup(
    name="RegexPicker plugin",
    version="0.1",
    author="Greg L. Turnquist",
    author_email="Greg.L.Turnquist@gmail.com",
    description="Pick test methods based on a regular expression",
    license="Apache Server License 2.0",
    py_modules=["plugin_RegexPicker"],
    entry_points = {
        'nose.plugins': [
            'plugin_RegexPicker = plugin_RegexPicker:RegexPicker'
            ]
    }
)