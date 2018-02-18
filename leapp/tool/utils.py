import json
import os
import re


def make_class_name(name):
    return ''.join(map(lambda x: x.capitalize(), re.split('[-_]', name)))


def make_name(name):
    return name.lower().replace('_', '-')


def find_project_basedir(path):
    path = os.path.realpath(path)
    while True:
        if os.path.isdir(os.path.join(path, '.leapp')):
            return path
        path, current = os.path.split(path)
        if not current:
            return None


def get_project_metadata(path):
    basedir = find_project_basedir(path)
    if basedir:
        with open(os.path.join(basedir, '.leapp', 'info'), 'r') as f:
            return json.load(f)
    return {}


def get_project_name(path):
    return get_project_metadata(path)['name']
