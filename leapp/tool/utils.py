import json
import os
import pkgutil
import re


def load_modules(pkg_path):
    modules = []
    for importer, name, is_pkg in pkgutil.iter_modules([pkg_path]):
        if is_pkg:
            continue
        modules.append(importer.find_module(name).load_module(name))
    return modules


def load_modules_from(path):
    if os.path.exists(path):
        if load_modules(path):
            return
        for root, _, _ in os.walk(path):
            if load_modules(root):
                return


def load_all_from(basedir):
    for directory in ('channels', 'models', 'actors'):  # Order is NOT arbitrary - keep the order
        modules_dir = os.path.join(basedir, directory)
        load_modules_from(modules_dir)


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
