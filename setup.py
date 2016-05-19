from setuptools import setup
import pip

install_reqs = pip.req.parse_requirements('requirements.txt',
                                          session=pip.download.PipSession())
reqs = [str(ir.req) for ir in install_reqs]

setup(
    name='pushpull',
    version='0.0.1',
    packages=['pushpull'],
    classifiers=[
        'License :: OSI Approved :: Apache Software License',
        'Intended Audience :: Developers',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Topic :: Internet :: WWW/HTTP'],
    author='Marco Paolini',
    author_email='markopaolini@gmail.com',
    url='https://github.com/elastic-coders/pushpull/',
    license='MIT',
    include_package_data=True,
    install_requires=reqs
)
