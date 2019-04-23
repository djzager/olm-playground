import time
from kubernetes import client, config
from openshift.dynamic import DynamicClient, exceptions

k8s_client = config.new_client_from_config()
dyn_client = DynamicClient(k8s_client)

# Create a namespace and return it's definition
def create_namespace(name):
    v1_namespaces = dyn_client.resources.get(
        api_version='v1',
        kind='Namespace'
    )
    namespace = {
        'kind': 'Namespace',
        'apiVersion': 'v1',
        'metadata': {
            'name': name
        }
    }
    try:
        print('Creating namespace')
        v1_namespaces.create(body=namespace)
    except exceptions.ConflictError:
        print("\tNamespace already exists")
    return v1_namespaces.get(name=name)

def create_operator_group(name, namespace):
    v1alpha2_operator_groups = dyn_client.resources.get(
        api_version='operators.coreos.com/v1alpha2',
        kind='OperatorGroup'
    )
    operator_group = {
        'apiVersion': 'operators.coreos.com/v1alpha2',
        'kind': 'OperatorGroup',
        'metadata': {
            'name': name,
            'namespace': namespace
        }
    }
    try:
        print('Creating operator group')
        v1alpha2_operator_groups.create(body=operator_group)
    except exceptions.ConflictError:
        print("\tOperator Group already exists")
    return v1alpha2_operator_groups.get(name=name, namespace=namespace)

def create_catalog_source(name, image, display_name):
    v1alpha1_catalog_sources = dyn_client.resources.get(
        api_version='operators.coreos.com/v1alpha1',
        kind='CatalogSource'
    )
    namespace = 'openshift-operator-lifecycle-manager'
    catalog_source = {
        'apiVersion': 'operators.coreos.com/v1alpha1',
        'kind': 'CatalogSource',
        'metadata': {
            'name': name,
            'namespace': namespace
        },
        'spec': {
            'sourceType': 'grpc',
            'image': image,
            'displayName': display_name,
            'publisher': 'Red Hat'
        }
    }
    try:
        print('Creating catalog source')
        v1alpha1_catalog_sources.create(catalog_source)
    except exceptions.ConflictError:
        print("\tCatalog source already exists")
    return v1alpha1_catalog_sources.get(name=name, namespace=namespace)

def patch_catalog_source(name, image, display_name):
    v1alpha1_catalog_sources = dyn_client.resources.get(
        api_version='operators.coreos.com/v1alpha1',
        kind='CatalogSource'
    )
    namespace = 'openshift-operator-lifecycle-manager'
    catalog_source = {
        'apiVersion': 'operators.coreos.com/v1alpha1',
        'kind': 'CatalogSource',
        'metadata': {
            'name': name,
            'namespace': namespace
        },
        'spec': {
            'sourceType': 'grpc',
            'image': image,
            'displayName': display_name,
            'publisher': 'Red Hat'
        }
    }
    try:
        print('Patching catalog source')
        v1alpha1_catalog_sources.patch(
            body=catalog_source,
            namespace=namespace,
            content_type='application/merge-patch+json'
        )
    except Exception as e:
        print('Something went wrong')
        raise(e)

def create_subscription(name, namespace, channel, catalog_source):
    # apiVersion: operators.coreos.com/v1alpha1
    # kind: Subscription
    # metadata:
    #     name: example-operator-a
    #     namespace: scenario1
    # spec:
    #     channel: alpha
    #     name: example-operator-a
    #     source: scenario1-catalogsource
    #     sourceNamespace: openshift-operator-lifecycle-manager
    #     startingCSV: example-operator-a.v0.0.1
    v1alpha1_subscriptions = dyn_client.resources.get(
        api_version='operators.coreos.com/v1alpha1',
        kind='Subscription'
    )
    subscription = {
        'apiVersion': 'operators.coreos.com/v1alpha1',
        'kind': 'Subscription',
        'metadata': {
            'name': name,
            'namespace': namespace
        },
        'spec': {
            'channel': channel,
            'name': name,
            'source': catalog_source,
            'sourceNamespace': 'openshift-operator-lifecycle-manager'
        }
    }
    try:
        print('Creating subscription')
        sub = v1alpha1_subscriptions.create(body=subscription)
    except exceptions.ConflictError:
        print("\tSubscription already exists")
    return v1alpha1_subscriptions.get(name=name, namespace=namespace)

def wait_ip_on_subscription(name, namespace):
    v1alpha1_subscriptions = dyn_client.resources.get(
        api_version='operators.coreos.com/v1alpha1',
        kind='Subscription'
    )
    print('Waiting for installplan')
    while True:
        subscription = v1alpha1_subscriptions.get(
            name=name,
            namespace=namespace
        )
        if not subscription['status']:
            print("\tNo status on subscription")
            time.sleep(10)
            continue
        if 'installplan' in subscription['status'].keys():
            return subscription['status']['installplan']['name']
        print("\tNo installplan found on subscription")
        time.sleep(10)

def wait_ip_complete(name, namespace):
    v1alpha1_install_plans = dyn_client.resources.get(
        api_version='operators.coreos.com/v1alpha1',
        kind='InstallPlan'
    )
    while True:
        install_plan = v1alpha1_install_plans.get(
            name=name,
            namespace=namespace
        )
        print(install_plan['status']['phase'])
        if install_plan['status']['phase'] == 'Complete':
            return
        time.sleep(10)

def dump_olm_bits(namespace, install_plan_name):
    v1_deployments = dyn_client.resources.get(
        api_version='apps/v1',
        kind='Deployment'
    )
    v1alpha1_subscriptions = dyn_client.resources.get(
        api_version='operators.coreos.com/v1alpha1',
        kind='Subscription'
    )
    v1alpha1_install_plans = dyn_client.resources.get(
        api_version='operators.coreos.com/v1alpha1',
        kind='InstallPlan'
    )
    # Print subscriptions
    print(v1alpha1_subscriptions.get(namespace=namespace))
    # Print install plan
    print(v1alpha1_install_plans.get(name=install_plan_name, namespace=namespace))
    # Print deployments
    print(v1_deployments.get(namespace=namespace))


