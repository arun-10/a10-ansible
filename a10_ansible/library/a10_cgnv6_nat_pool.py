#!/usr/bin/python

# Copyright 2018 A10 Networks
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

REQUIRED_NOT_SET = (False, "One of ({}) must be set.")
REQUIRED_MUTEX = (False, "Only one of ({}) can be set.")
REQUIRED_VALID = (True, "")


DOCUMENTATION = """
module: a10_cgnv6_nat_pool
description:
    - Configure CGNv6 NAT pool
short_description: Configures A10 cgnv6.nat.pool
author: A10 Networks 2018 
version_added: 2.4
options:
    state:
        description:
        - State of the object to be created.
        choices:
        - present
        - absent
        required: True
    a10_host:
        description:
        - Host for AXAPI authentication
        required: True
    a10_username:
        description:
        - Username for AXAPI authentication
        required: True
    a10_password:
        description:
        - Password for AXAPI authentication
        required: True
    partition:
        description:
        - Destination/target partition for object/command
    all:
        description:
        - "Share with all partitions"
        required: False
    tcp_time_wait_interval:
        description:
        - "Minutes before TCP NAT ports can be reused"
        required: False
    group:
        description:
        - "Share with a partition group (Partition Group Name)"
        required: False
    uuid:
        description:
        - "uuid of the object"
        required: False
    start_address:
        description:
        - "Configure start IP address of NAT pool"
        required: False
    per_batch_port_usage_warning_threshold:
        description:
        - "Configure warning log threshold for per batch port usage (default= disabled) (Number of ports)"
        required: False
    vrid:
        description:
        - "Configure VRRP-A vrid (Specify ha VRRP-A vrid)"
        required: False
    usable_nat_ports_start:
        description:
        - "Start Port of Usable NAT Ports (needs to be even)"
        required: False
    usable_nat_ports_end:
        description:
        - "End Port of Usable NAT Ports"
        required: False
    partition:
        description:
        - "Share with a single partition (Partition Name)"
        required: False
    netmask:
        description:
        - "Configure mask for pool"
        required: False
    max_users_per_ip:
        description:
        - "Number of users that can be assigned to a NAT IP"
        required: False
    simultaneous_batch_allocation:
        description:
        - "Allocate same TCP and UDP batches at once"
        required: False
    shared:
        description:
        - "Share this pool with other partitions (default= not shared)"
        required: False
    port_batch_v2_size:
        description:
        - "'64'= Allocate 64 ports at a time; '128'= Allocate 128 ports at a time; '256'= Allocate 256 ports at a time; '512'= Allocate 512 ports at a time; '1024'= Allocate 1024 ports at a time; '2048'= Allocate 2048 ports at a time; '4096'= Allocate 4096 ports at a time; "
        required: False
    end_address:
        description:
        - "Configure end IP address of NAT pool"
        required: False
    usable_nat_ports:
        description:
        - "Configure usable NAT ports"
        required: False
    exclude_ip:
        description:
        - "Field exclude_ip"
        required: False
        suboptions:
            exclude_ip_start:
                description:
                - "Single IP address or IP address range start"
            exclude_ip_end:
                description:
                - "Address range end"
    pool_name:
        description:
        - "Specify pool name or pool group"
        required: True

"""

EXAMPLES = """
"""

ANSIBLE_METADATA = {
    'metadata_version': '1.1',
    'supported_by': 'community',
    'status': ['preview']
}

# Hacky way of having access to object properties for evaluation
AVAILABLE_PROPERTIES = ["all","end_address","exclude_ip","group","max_users_per_ip","netmask","partition","per_batch_port_usage_warning_threshold","pool_name","port_batch_v2_size","shared","simultaneous_batch_allocation","start_address","tcp_time_wait_interval","usable_nat_ports","usable_nat_ports_end","usable_nat_ports_start","uuid","vrid",]

# our imports go at the top so we fail fast.
try:
    from a10_ansible import errors as a10_ex
    from a10_ansible.axapi_http import client_factory, session_factory
    from a10_ansible.kwbl import KW_IN, KW_OUT, translate_blacklist as translateBlacklist

except (ImportError) as ex:
    module.fail_json(msg="Import Error:{0}".format(ex))
except (Exception) as ex:
    module.fail_json(msg="General Exception in Ansible module import:{0}".format(ex))


def get_default_argspec():
    return dict(
        a10_host=dict(type='str', required=True),
        a10_username=dict(type='str', required=True),
        a10_password=dict(type='str', required=True, no_log=True),
        state=dict(type='str', default="present", choices=["present", "absent"]),
        a10_port=dict(type='int', required=True),
        a10_protocol=dict(type='str', choices=["http", "https"]),
        partition=dict(type='str', required=False)
    )

def get_argspec():
    rv = get_default_argspec()
    rv.update(dict(
        all=dict(type='bool',),
        tcp_time_wait_interval=dict(type='int',),
        group=dict(type='str',),
        uuid=dict(type='str',),
        start_address=dict(type='str',),
        per_batch_port_usage_warning_threshold=dict(type='int',),
        vrid=dict(type='int',),
        usable_nat_ports_start=dict(type='int',),
        usable_nat_ports_end=dict(type='int',),
        partition=dict(type='str',),
        netmask=dict(type='str',),
        max_users_per_ip=dict(type='int',),
        simultaneous_batch_allocation=dict(type='bool',),
        shared=dict(type='bool',),
        port_batch_v2_size=dict(type='str',choices=['64','128','256','512','1024','2048','4096']),
        end_address=dict(type='str',),
        usable_nat_ports=dict(type='bool',),
        exclude_ip=dict(type='list',exclude_ip_start=dict(type='str',),exclude_ip_end=dict(type='str',)),
        pool_name=dict(type='str',required=True,)
    ))
   

    return rv

def new_url(module):
    """Return the URL for creating a resource"""
    # To create the URL, we need to take the format string and return it with no params
    url_base = "/axapi/v3/cgnv6/nat/pool/{pool-name}"

    f_dict = {}
    f_dict["pool-name"] = ""

    return url_base.format(**f_dict)

def existing_url(module):
    """Return the URL for an existing resource"""
    # Build the format dictionary
    url_base = "/axapi/v3/cgnv6/nat/pool/{pool-name}"

    f_dict = {}
    f_dict["pool-name"] = module.params["pool_name"]

    return url_base.format(**f_dict)


def build_envelope(title, data):
    return {
        title: data
    }

def _to_axapi(key):
    return translateBlacklist(key, KW_OUT).replace("_", "-")

def _build_dict_from_param(param):
    rv = {}

    for k,v in param.items():
        hk = _to_axapi(k)
        if isinstance(v, dict):
            v_dict = _build_dict_from_param(v)
            rv[hk] = v_dict
        elif isinstance(v, list):
            nv = [_build_dict_from_param(x) for x in v]
            rv[hk] = nv
        else:
            rv[hk] = v

    return rv

def build_json(title, module):
    rv = {}

    for x in AVAILABLE_PROPERTIES:
        v = module.params.get(x)
        if v:
            rx = _to_axapi(x)

            if isinstance(v, dict):
                nv = _build_dict_from_param(v)
                rv[rx] = nv
            elif isinstance(v, list):
                nv = [_build_dict_from_param(x) for x in v]
                rv[rx] = nv
            else:
                rv[rx] = module.params[x]

    return build_envelope(title, rv)

def validate(params):
    # Ensure that params contains all the keys.
    requires_one_of = sorted([])
    present_keys = sorted([x for x in requires_one_of if x in params])
    
    errors = []
    marg = []
    
    if not len(requires_one_of):
        return REQUIRED_VALID

    if len(present_keys) == 0:
        rc,msg = REQUIRED_NOT_SET
        marg = requires_one_of
    elif requires_one_of == present_keys:
        rc,msg = REQUIRED_MUTEX
        marg = present_keys
    else:
        rc,msg = REQUIRED_VALID
    
    if not rc:
        errors.append(msg.format(", ".join(marg)))
    
    return rc,errors

def get(module):
    return module.client.get(existing_url(module))

def exists(module):
    try:
        return get(module)
    except a10_ex.NotFound:
        return False

def create(module, result):
    payload = build_json("pool", module)
    try:
        post_result = module.client.post(new_url(module), payload)
        if post_result:
            result.update(**post_result)
        result["changed"] = True
    except a10_ex.Exists:
        result["changed"] = False
    except a10_ex.ACOSException as ex:
        module.fail_json(msg=ex.msg, **result)
    except Exception as gex:
        raise gex
    return result

def delete(module, result):
    try:
        module.client.delete(existing_url(module))
        result["changed"] = True
    except a10_ex.NotFound:
        result["changed"] = False
    except a10_ex.ACOSException as ex:
        module.fail_json(msg=ex.msg, **result)
    except Exception as gex:
        raise gex
    return result

def update(module, result, existing_config):
    payload = build_json("pool", module)
    try:
        post_result = module.client.post(existing_url(module), payload)
        if post_result:
            result.update(**post_result)
        if post_result == existing_config:
            result["changed"] = False
        else:
            result["changed"] = True
    except a10_ex.ACOSException as ex:
        module.fail_json(msg=ex.msg, **result)
    except Exception as gex:
        raise gex
    return result

def present(module, result, existing_config):
    if not exists(module):
        return create(module, result)
    else:
        return update(module, result, existing_config)

def absent(module, result):
    return delete(module, result)

def replace(module, result, existing_config):
    payload = build_json("pool", module)
    try:
        post_result = module.client.put(existing_url(module), payload)
        if post_result:
            result.update(**post_result)
        if post_result == existing_config:
            result["changed"] = False
        else:
            result["changed"] = True
    except a10_ex.ACOSException as ex:
        module.fail_json(msg=ex.msg, **result)
    except Exception as gex:
        raise gex
    return result

def run_command(module):
    run_errors = []

    result = dict(
        changed=False,
        original_message="",
        message=""
    )

    state = module.params["state"]
    a10_host = module.params["a10_host"]
    a10_username = module.params["a10_username"]
    a10_password = module.params["a10_password"]
    a10_port = module.params["a10_port"] 
    a10_protocol = module.params["a10_protocol"]
    
    partition = module.params["partition"]

    valid = True

    if state == 'present':
        valid, validation_errors = validate(module.params)
        map(run_errors.append, validation_errors)
    
    if not valid:
        result["messages"] = "Validation failure"
        err_msg = "\n".join(run_errors)
        module.fail_json(msg=err_msg, **result)

    module.client = client_factory(a10_host, a10_port, a10_protocol, a10_username, a10_password)
    if partition:
        module.client.activate_partition(partition)

    existing_config = exists(module)

    if state == 'present':
        result = present(module, result, existing_config)
        module.client.session.close()
    elif state == 'absent':
        result = absent(module, result)
        module.client.session.close()
    return result

def main():
    module = AnsibleModule(argument_spec=get_argspec())
    result = run_command(module)
    module.exit_json(**result)

# standard ansible module imports
from ansible.module_utils.basic import *
from ansible.module_utils.urls import *

if __name__ == '__main__':
    main()