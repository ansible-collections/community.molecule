"""Ansible Molecule Filters."""

from __future__ import absolute_import, division, print_function

import os

# TODO(ssbarnea): Must remove the dependency on molecule python module here
try:
    from molecule import config, interpolation, util

    MOLECULE_IMPORT_ERROR = None
except ImportError as imp_exc:
    MOLECULE_IMPORT_ERROR = imp_exc

from ansible.errors import AnsibleError
from ansible.module_utils.six import raise_from

__metaclass__ = type


def from_yaml(data):
    """
    Interpolate the provided data and return a dict.

    Currently, this is used to re-interpolate the `molecule.yml` inside an
    Ansible playbook.  If there were any interpolation errors, they would
    have been found and raised earlier.

    :return: dict
    """
    molecule_env_file = os.environ.get("MOLECULE_ENV_FILE", None)

    env = os.environ.copy()
    if molecule_env_file:
        env = config.set_env_from_file(env, molecule_env_file)

    i = interpolation.Interpolator(interpolation.TemplateWithDefaults, env)
    interpolated_data = i.interpolate(data)

    return util.safe_load(interpolated_data)


def to_yaml(data):
    """Format data as YAML."""
    return str(util.safe_dump(data))


def header(content):
    """Prepend molecule header."""
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


class FilterModule(object):
    """Core Molecule filter plugins."""

    def filters(self):
        """Return implemented filters."""
        # if MOLECULE_IMPORT_ERROR:
        #     raise_from(
        #         AnsibleError(
        #             "molecule python package must be installed to use this plugin"
        #         ),
        #         MOLECULE_IMPORT_ERROR,
        #     )

        return {
            "from_yaml": from_yaml,
            "to_yaml": to_yaml,
            "header": header,
            "get_docker_networks": get_docker_networks,
        }
