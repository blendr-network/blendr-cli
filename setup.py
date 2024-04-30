from setuptools import setup, find_packages
import os

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name='blendr-cli',
    version='0.1.4',
    packages=find_packages(),
    install_requires=[
        'click',      
        'requests',  
        'colorama',
        'GPUtil',
        'psutil',
        'keyring'
    ],
    entry_points={
        'console_scripts': [
            'blendr=blendr.cli:main'
        ]
    },
    author='Blendr Network',
    author_email='tech@blendr.network',
    description='Blendr CLI tool for GPU Lending',
    license='MIT',
    keywords='blendr cli',
    url='https://www.blendr.network',  # Optional project URL
    long_description=read('README.md'),
    long_description_content_type='text/markdown',
)
