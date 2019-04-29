import time
from kubernetes import client, config
from openshift.dynamic import DynamicClient, exceptions

k8s_client = config.new_client_from_config()
dyn_client = DynamicClient(k8s_client)

olm_namespace = 'openshift-operator-lifecycle-manager'

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

def delete_namespace(name):
    v1_namespaces = dyn_client.resources.get(
        api_version='v1',
        kind='Namespace'
    )
    try:
        print('Deleting namespace')
        v1_namespaces.delete(name=name)
    except exceptions.NotFoundError:
        print("\tNamespace already removed")

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

def delete_operator_group(name, namespace):
    v1alpha2_operator_groups = dyn_client.resources.get(
        api_version='operators.coreos.com/v1alpha2',
        kind='OperatorGroup'
    )
    try:
        print('Deleting operator group')
        v1alpha2_operator_groups.delete(name=name, namespace=namespace)
    except exceptions.NotFoundError:
        print("\tOperator Group already removed")

def create_catalog_source(name, image, display_name):
    v1alpha1_catalog_sources = dyn_client.resources.get(
        api_version='operators.coreos.com/v1alpha1',
        kind='CatalogSource'
    )
    catalog_source = {
        'apiVersion': 'operators.coreos.com/v1alpha1',
        'kind': 'CatalogSource',
        'metadata': {
            'name': name,
            'namespace': olm_namespace
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
    return v1alpha1_catalog_sources.get(name=name, namespace=olm_namespace)

def patch_catalog_source(name, image):
    v1alpha1_catalog_sources = dyn_client.resources.get(
        api_version='operators.coreos.com/v1alpha1',
        kind='CatalogSource'
    )
    catalog_source = {
        'apiVersion': 'operators.coreos.com/v1alpha1',
        'kind': 'CatalogSource',
        'metadata': {
            'name': name,
            'namespace': olm_namespace
        },
        'spec': {
            'image': image
        }
    }
    try:
        print('Patching catalog source')
        v1alpha1_catalog_sources.patch(
            body=catalog_source,
            namespace=olm_namespace,
            content_type='application/merge-patch+json'
        )
    except Exception as e:
        print('Something went wrong')
        raise(e)

    # TODO: Workaround until https://github.com/operator-framework/operator-lifecycle-manager/pull/816
    v1_pods = dyn_client.resources.get(
        api_version='v1',
        kind='Pod'
    )
    registry_pod_list = v1_pods.get(namespace=olm_namespace, label_selector='olm.catalogSource=' + name)
    registry_pods = registry_pod_list.to_dict()
    registry_pod_def = registry_pods['items'][0]
    registry_pod_def['spec']['containers'][0]['image'] = image
    v1_pods.patch(
        body=registry_pod_def,
        namespace=olm_namespace,
        content_type='application/merge-patch+json'
    )

    return v1alpha1_catalog_sources.get(name=name, namespace=olm_namespace)


def delete_catalog_source(name):
    v1alpha1_catalog_sources = dyn_client.resources.get(
        api_version='operators.coreos.com/v1alpha1',
        kind='CatalogSource'
    )
    try:
        print('Deleting catalog source')
        v1alpha1_catalog_sources.delete(name=name, namespace=olm_namespace)
    except exceptions.NotFoundError:
        print("\tCatalog source already removed")

# def create_subscription(name, namespace, channel, catalog_source, starting_csv=None):
def create_subscription(name, namespace, channel, catalog_source):
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
    # if starting_csv:
    #     subscription['spec']['startingCSV'] = starting_csv
    try:
        print('Creating subscription')
        sub = v1alpha1_subscriptions.create(body=subscription)
    except exceptions.ConflictError:
        print("\tSubscription already exists")
    return v1alpha1_subscriptions.get(name=name, namespace=namespace)

def delete_subscription(name, namespace):
    v1alpha1_subscriptions = dyn_client.resources.get(
        api_version='operators.coreos.com/v1alpha1',
        kind='Subscription'
    )
    try:
        print('Deleting subscription')
        v1alpha1_subscriptions.delete(name=name, namespace=namespace)
    except exceptions.NotFoundError:
        print("\tSubscription already removed")

def wait_ip_on_subscription(name, namespace):
    v1alpha1_subscriptions = dyn_client.resources.get(
        api_version='operators.coreos.com/v1alpha1',
        kind='Subscription'
    )
    print('Waiting for installplan')
    start_time = time.time()
    while True:
        subscription = v1alpha1_subscriptions.get(
            name=name,
            namespace=namespace
        )
        if not subscription['status']:
            elapsed_time = time.time() - start_time
            print("\tNo status on subscription - time elapsed: " + time.strftime("%H:%M:%S", time.gmtime(elapsed_time)))
            time.sleep(30)
            continue
        if 'installplan' in subscription['status'].keys():
            return subscription['status']['installplan']['name']
        print("\tNo installplan found on subscription")
        time.sleep(30)

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


