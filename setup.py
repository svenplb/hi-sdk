from setuptools import setup, find_packages

setup(
    name='hi-sdk',
    version='0.1',
    description='LLM Development Kit for Raspberry Pi',
    author='Your Name',
    author_email='psven595@gmail.com',
    url='https://github.com/svenplb/hi-sdk',
    packages=find_packages(),
    install_requires=[
        'requests',
        'fastapi',
        'uvicorn',
        'click',
        'colorama',
        'pydantic'
    ],
    entry_points={
        'console_scripts': [
            'hi=sdk.cli:main',
        ],
    },
    python_requires='>=3.7',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 3',
    ],
)
