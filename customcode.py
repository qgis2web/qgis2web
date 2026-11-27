"""User-owned JavaScript and CSS extension points for qgis2web exports."""

import os
import shutil


CUSTOM_CODE_DIR = 'custom_code'
CUSTOM_CODE_FILES = ('custom.js', 'custom.css')
PLUGIN_ROOT = os.path.dirname(os.path.abspath(__file__))
CUSTOM_CODE_ROOT = os.path.join(PLUGIN_ROOT, CUSTOM_CODE_DIR)
CUSTOM_CODE_TEMPLATE_VALUES = {
    '@CUSTOMCSS@': '<link rel="stylesheet" href="./custom_code/custom.css">',
    '@CUSTOMJS@': '<script src="./custom_code/custom.js"></script>',
}


def custom_code_folder(folder):
    return os.path.join(folder, CUSTOM_CODE_DIR)


def copy_custom_code(folder, overwrite=True):
    destination_folder = custom_code_folder(folder)
    written = []
    for name in CUSTOM_CODE_FILES:
        destination = os.path.join(destination_folder, name)
        if not overwrite and os.path.exists(destination):
            continue
        source = os.path.join(CUSTOM_CODE_ROOT, name)
        if os.path.isfile(source) and \
                os.path.abspath(source) == os.path.abspath(destination):
            continue
        os.makedirs(destination_folder, exist_ok=True)
        if os.path.isfile(source):
            shutil.copyfile(source, destination)
        else:
            with open(destination, 'a', encoding='utf-8'):
                pass
        written.append(name)
    return written


def ensure_custom_code(folder):
    return copy_custom_code(folder, overwrite=False)