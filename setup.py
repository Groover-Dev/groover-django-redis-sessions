import sys

from setuptools import setup


packages = [
    'redis_sessions_fork',
    'redis_sessions_fork.management',
    'redis_sessions_fork.management.commands'
]


install_requires = [
    'redis>=2.4.10',
    'django>=1.3',
    'django_appconf>=0.6'
]


if not '__pypy__' in sys.builtin_module_names:
    install_requires.append('hiredis>=0.1.1')


setup(
    name='django-redis-sessions-fork',
    version='0.6.3',
    description='Redis Session Backend For Django',
    long_description=open('README.rst').read(),
    keywords='django, sessions, redis',
    author='see AUTHORS',
    author_email='hellysmile@gmail.com',
    url='https://github.com/hellysmile/django-redis-sessions-fork',
    license='BSD',
    packages=packages,
    zip_safe=False,
    install_requires=install_requires,
    include_package_data=True,
    classifiers=[
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Framework :: Django',
        'Environment :: Web Environment',
    ],
)
