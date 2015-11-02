import ast
import os
import codecs
import sys
from setuptools import setup


class VersionFinder(ast.NodeVisitor):
    def __init__(self):
        self.version = None

    def visit_Assign(self, node):  # noqa
        if node.targets[0].id == '__version__':
            self.version = node.value.s


def read(*parts):
    filename = os.path.join(os.path.dirname(__file__), *parts)
    with codecs.open(filename, encoding='utf-8') as fp:
        return fp.read()


def find_version(*parts):
    finder = VersionFinder()
    finder.visit(ast.parse(read(*parts)))
    return finder.version


packages = [
    'redis_sessions_fork',
    'redis_sessions_fork.management',
    'redis_sessions_fork.management.commands'
]


install_requires = [
    'redis',
    'django',
    'django_appconf'
]


if '__pypy__' not in sys.builtin_module_names:
    install_requires.append('hiredis')


if sys.version_info[0:2] < (2, 7):
    install_requires.append('importlib')


setup(
    name='django-redis-sessions-fork',
    version=find_version('redis_sessions_fork', '__init__.py'),
    description='Redis Session Backend For Django',
    long_description=read('README.rst'),
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
