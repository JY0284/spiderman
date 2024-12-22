# setup.py

from setuptools import setup, find_packages

setup(
    name='data-collection-notification',
    version='0.1.1',
    packages=find_packages(),
    install_requires=[
        'schedule',
        'requests',
        'beautifulsoup4',
        'pytz',
        'matplotlib',
        'pandas',
        'seaborn',
        'Jinja2',
    ],
    entry_points={
        'console_scripts': [
            'dc-notifier=scheduler.scheduler:main',
        ],
    },
    author='Your Name',
    author_email='your.email@example.com',
    description='A data collection and notification system.',
    license='MIT',
    keywords='data collection notification',
    url='https://github.com/yourusername/data-collection-notification',
)
