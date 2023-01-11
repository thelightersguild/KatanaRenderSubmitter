from setuptools import setup

VERSION = '0.0.2'
DESCRIPTION = 'Render submitter for Katana'

# Setting up
setup(
    name="KatanaRenderSubmitter",
    version=VERSION,
    author="jlonghurst",
    url="https://github.com/thelightersguild/KatanaRenderSubmitter",
    description=DESCRIPTION,
    py_modules=["core", 'ui', 'util'],
    #long_description=open('README.md').read + '/n/n' +open('CHANELOG.txt').read(),
    install_requires=[],
    #package_dir={'bin': 'katana_render_submitter'},
    packages=['katana_render_submitter', 'katana_render_submitter/Tabs'],
    classifiers=["Programming Language :: Python :: 3"],
)