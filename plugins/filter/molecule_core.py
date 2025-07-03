"""Ansible Molecule Filters."""

from __future__ import absolute_import, division, print_function

import os

__metaclass__ = type  # pylint: disable=invalid-name
# pylint: skip-file

DOCUMENTATION = """
name: from_yaml
description:
    - This callback just adds total play duration to the play stats.
"""
try:
    from molecule import config, interpolation, util

    MOLECULE_IMPORT_ERROR = None
except ImportError as imp_exc:
    MOLECULE_IMPORT_ERROR = imp_exc


def from_yaml(data):
    """
    Interpolate the provided data and return a dict.

    Currently, this is used to re-interpolate the `molecule.yml` inside an
    Ansible playbook.  If there were any interpolation errors, they would
    have been found and raised earlier.

    :return: dict
    """
    if MOLECULE_IMPORT_ERROR:
        return None

    molecule_env_file = os.environ.get("MOLECULE_ENV_FILE", None)

    env = os.environ.copy()
    if molecule_env_file:
        env = config.set_env_from_file(env, molecule_env_file)  # pylint: disable=undefined-variable

    i = interpolation.Interpolator(interpolation.TemplateWithDefaults, env)  # pylint: disable=undefined-variable
    interpolated_data = i.interpolate(data)

    return util.safe_load(interpolated_data)  # pylint: disable=undefined-variable


def to_yaml(data):
    """Format data as YAML."""
    if MOLECULE_IMPORT_ERROR:
        return ""

    return util.safe_dump(data)  # pylint: disable=undefined-variable


def header(content):
    """Prepend molecule header."""
    if MOLECULE_IMPORT_ERROR:
        return ""

    return util.molecule_prepender(content)


def get_docker_networks(data, state, labels=None):
    """Get list of docker networks."""
    network_list = []
    network_names = []
    if not labels:
        labels = {}
    for platform in data:
        if "docker_networks" in platform:
            for docker_network in platform["docker_networks"]:
                if "labels" not in docker_network:
                    docker_network["labels"] = {}
                for key in labels:
                    docker_network["labels"][key] = labels[key]

                docker_network["state"] = state

                if "name" in docker_network:
                    network_list.append(docker_network)
                    network_names.append(docker_network["name"])

        # If a network name is defined for a platform but is not defined in
        # docker_networks, add it to the network list.
        if "networks" in platform:
            for network in platform["networks"]:
                if "name" in network:
                    name = network["name"]
                    if name not in network_names:
                        network_list.append({
                            "name": name,
                            "labels": labels,
                            "state": state,
                        })
    return network_list


class FilterModule:
    """Core Molecule filter plugins."""

    def filters(self):
        """Return implemented filters."""

        return {
            "from_yaml": from_yaml,
            "to_yaml": to_yaml,
            "header": header,
            "get_docker_networks": get_docker_networks,
        }
