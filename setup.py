from setuptools import setup, find_packages
import pip
import os

install_reqs = pip.req.parse_requirements('requirements.txt',
                                          session=pip.download.PipSession())
reqs = [str(ir.req) for ir in install_reqs]

with open(os.path.join(os.path.dirname(__file__), 'README.rst')) as readme_f:
    long_description = readme_f.read()


setup(
    name='pushpull',
    version='0.0.2',
    packages=find_packages(),
    description='Websocket to message broker gateway',
    long_description=long_description,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Intended Audience :: Developers',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Software Development :: Libraries :: Python Modules'],
    author='Marco Paolini',
    author_email='markopaolini@gmail.com',
    url='https://github.com/elastic-coders/pushpull/',
    license='MIT',
    keywords=['websocket', 'asyncio', 'rabbitmq'],
    include_package_data=True,
    install_requires=reqs,
    entry_points={
        'console_scripts': [
            'pushpull-server = pushpull.cli.server:serve',
            'pushpull-client = pushpull.cli.client:client',
        ]
    }
)
