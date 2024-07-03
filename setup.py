from setuptools import setup, find_packages
import os

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name='blendr-cli',
    version='0.2.0',
    packages=find_packages(),
    install_requires=[
        'click==8.1.7',
        'requests==2.31.0',
        'colorama==0.4.6',
        'psutil==5.9.8',
        'python-socketio[client]==5.11.2',
        'keyring==25.2.0',
        'keyrings.alt==5.0.1',
        'speedtest-cli==2.1.3',
        'pandas==2.2.2',
        'transformers==4.40.2',
        'datasets==2.19.1',
        'py3nvml==0.2.7'
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
    keywords='blendr cli gpu lending',
    url='https://www.blendr.network',
    long_description=read('README.md'),
    long_description_content_type='text/markdown',
)