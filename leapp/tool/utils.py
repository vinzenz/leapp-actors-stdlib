import os


def find_project_basedir(path):
    path = os.path.realpath(path)
    while True:
        if os.path.isfile(os.path.join(path, '.leapp')):
            return path
        path, current = os.path.split(path)
        if not current:
            return None
