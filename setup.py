from setuptools import setup, find_packages

setup(
    name='blendr-cli',
    version='0.1.0',
    packages=find_packages(),
    install_requires=[
        'click',      
        'requests',  
        'colorama'    
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
)
