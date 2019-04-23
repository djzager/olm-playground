#!/usr/bin/env python

import common

name = 'scenario1'
v1image = 'docker.io/djzager/olm-playground-scenario1:v1'
v2image = 'docker.io/djzager/olm-playground-scenario1:v2'
operator_name = 'example-operator-a'
operator_subscription = {
    'name': operator_name,
    'namespace': name,
    'channel': 'alpha',
    'catalog_source': name
}

common.create_namespace(name=name)
common.create_operator_group(name=name, namespace=name)
common.create_catalog_source(name=name, image=v1image, display_name='Scenario 1 Catalog Source')
common.create_subscription(**operator_subscription)

install_plan_name = common.wait_ip_on_subscription(name=operator_name, namespace=name)
common.wait_ip_complete(name=install_plan_name, namespace=name)
common.dump_olm_bits(namespace=name, install_plan_name=install_plan_name)

common.patch_catalog_source(name=name, image=v2image, display_name='Scenario 1 Catalog Source')
