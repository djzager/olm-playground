#!/usr/bin/env python

import argparse
import common

name = 'scenario3'
operator_a_name = 'example-operator-a'
operator_a_namespace = name
operator_a_subscription = {
    'name': operator_a_name,
    'namespace': operator_a_namespace,
    'channel': 'stable',
    'catalog_source': name
}
v1image = 'docker.io/djzager/olm-playground-scenario3:v1'

def run():
    # Set scenario baseline:
    # namespaces + operator groups + catalog source
    common.create_namespace(name=operator_a_namespace)
    common.create_operator_group(name=operator_a_name, namespace=operator_a_namespace)
    common.create_catalog_source(name=name, image=v1image, display_name=name)

    # Subscribe to operator a (remember that it depends on operator b)
    #common.create_subscription(**operator_a_subscription)
    #install_plan_name = common.wait_ip_on_subscription(name=operator_a_name, namespace=operator_a_namespace)
    #common.wait_ip_complete(name=install_plan_name, namespace=operator_a_namespace)
    # Show the current status of olm objects
    #common.dump_olm_bits(namespace=operator_a_namespace, install_plan_name=install_plan_name)

def teardown():
    # Remove subscriptions
    common.delete_subscription(name=operator_a_name, namespace=operator_a_namespace)

    # Remove the catalog
    common.delete_catalog_source(name=name)

    # Remove the operator groups
    common.delete_operator_group(name=operator_a_name, namespace=operator_a_namespace)

    # Remove the namespaces
    common.delete_namespace(name=operator_a_namespace)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='OLM Playground Scenario Runner')
    parser.add_argument('command', choices=['run', 'teardown'])
    args = parser.parse_args()
    locals()[args.command]()

