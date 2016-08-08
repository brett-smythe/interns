"""Setup for interns service"""
from codecs import open as cod_open
from setuptools import setup, find_packages


with cod_open('README.md', encoding='utf-8') as inf:
    long_description = inf.read()

reqs = []
with open('requirements.txt') as inf:
    for line in inf:
        line = line.strip()
        reqs.append(line)

setup(
    name='interns',
    version='0.3.1',
    description='Worker to gather text sources for related projects',
    long_description=long_description,
    author='Brett Smythe',
    author_email='smythebrett@gmail.com',
    maintainer='Brett Smythe',
    maintainer_email='smythebrett@gmail.com',
    url='https://github.com/brett-smythe/interns',
    packages=find_packages(),
    install_requires=reqs,
    entry_points={
        'console_scripts': [
            'interns = interns.main:run_scheduler'
        ]
    }
)
