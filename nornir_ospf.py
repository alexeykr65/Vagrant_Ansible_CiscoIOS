#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Configure S-Terra
#
# alexeykr@gmail.com
# coding=utf-8
# import codecs

"""
Runbook to configure labs
"""
import jinja2 as j2
import yaml
import logging
from nornir import InitNornir
from nornir.plugins.functions.text import (
    print_result, print_title
)
from nornir.plugins.tasks.data import load_yaml
from nornir.plugins.tasks.networking import netmiko_send_config, napalm_configure, netmiko_send_command
from nornir.plugins.tasks.text import template_file
from netaddr import IPNetwork
import ipdb
import re
import argparse
from termcolor import colored
# ipdb.set_trace()


def check_argument_parser():
    description_argument_parser = ""
    epilog_argument_parser = ""
    parser = argparse.ArgumentParser(description=description_argument_parser, epilog=epilog_argument_parser)
    parser.add_argument('-pl', '--ploop', help='Ping loop interfaces', dest="ploop", action="store_true")
    parser.add_argument('-io', '--info_ospf', help='Get information from OSPF', dest="info_ospf", action="store_true")
    parser.add_argument('-o', '--ospf', help='OSPF Configure Standart ', dest="ospf", action="store_true")
    parser.add_argument('-c', '--cmd', help='Run command on Routers', dest="cmd", default='')
    parser.add_argument('-f', '--filter', help='Filter for output information', dest="filter", default='')

    return parser.parse_args()


def ipaddr(input, net_cfg):
    ip_net = IPNetwork(input)
    if net_cfg == 'address':
        return ip_net.ip
    elif net_cfg == 'netmask':
        return ip_net.netmask
    elif net_cfg == 'hostmask':
        return ip_net.hostmask
    elif net_cfg == 'network':
        return ip_net.network


def ping_check_base(task):
    r = task.run(
        name="Ping check",
        task=netmiko_send_command,
        command_string="ping 20.2.4.2"
    )
    if re.match(".*Success\srate\sis\s0.*", r.result, re.DOTALL):
        print(f'Host: {str(task.host)} ping Failed')
    else:
        print(f'Host: {str(task.host)} ping OK')


def run_command_vios(task, cmd):

    # task.host['ping'] = dt['ping_check_loop'][str(task.host)]
    # print_result(task.host)
    task.run(
        name=f'{cmd}',
        task=netmiko_send_command,
        command_string=cmd
    )


def ping_check_loop(task, dt):
    # task.host['ping'] = dt['ping_check_loop'][str(task.host)]
    # print_result(task.host)
    for ph in dt['ping_check_loop'][str(task.host)]:
        cmd = f'ping {ph} repeat 3'
        task.run(
            name=f'Ping {ph}',
            task=netmiko_send_command,
            command_string=cmd
        )
        # if re.match(".*Success\srate\sis\s0.*", r.result, re.DOTALL):
        #     print(f'Host: {str(task.host)} ping Failed')
        # else:
        #     print(f'Host: {str(task.host)} ping OK')

    # config = r.result

    # if re.match(".*Success\srate\sis\s0.*", r.result, re.DOTALL):
    #     print(f'Host: {str(task.host)} ping Failed')
    # else:
    #     print(f'Host: {str(task.host)} ping OK')


def configure(task, dt):
    """
    This function groups all the tasks needed to configure the network
    """

    task.host['networks'] = dt['networks'][str(task.host)]
    # print_result(task.host)
    r = task.run(
        name="Configure OSPF",
        task=template_file,
        template="ospf_01.j2",
        path=f'templates',
        # severity_level=logging.ERROR
    )
    config = r.result

    task.run(
        name="Loading Configuration on the device",
        task=netmiko_send_config,
        config_commands=config,
    )


def get_info_ospf(task, ospf):
    cmd = f'show ip ospf nei'
    r = task.run(
        name=f'Command: {cmd}',
        task=netmiko_send_command,
        command_string=cmd
        # severity_level=logging.ERROR
    )
    pattern = r'''
            (?P<rid>\d+\.\d+\.\d+\.\d+)\s+
            (?P<priority>\d+)\s+
            (?P<state>\w+)/\s*
            (?P<role>[A-Z-]+)\s+
            (?P<deadtime>[0-9:]+|-)\s+
            (?P<peer>\d+\.\d+\.\d+\.\d+)\s+
            (?P<intf>[0-9A-Za-z./_-]+)
        '''
    inf_nei = r.result
    regex = re.compile(pattern, re.VERBOSE)
    ospf_neighbors = []
    if inf_nei:
        ospf[str(task.host)] = dict()
        for line in inf_nei.split('\n'):
            match = regex.search(line)
            if match:
                gdict = match.groupdict()
                # gdict['priority'] = FilterModule._try_int(gdict['priority'])
                gdict['state'] = gdict['state'].lower()
                gdict['role'] = gdict['role'].lower()
                gdict['intf'] = gdict['intf'].lower()
                ospf_neighbors.append(gdict)
        ospf[str(task.host)]['neighbor'] = ospf_neighbors

    #########################################################
    # Check command 'show ip ospf database database-summary'
    cmd = f'show ip ospf'
    r = task.run(
        name=f'Command: {cmd}',
        task=netmiko_send_command,
        command_string=cmd
        # severity_level=logging.ERROR
    )
    inf_nei = r.result

    process_pattern = r'''
        Routing\s+Process\s+"ospf\s+(?P<id>\d+)"\s+with\s+ID\s+(?P<rid>\d+\.\d+\.\d+\.\d+)
        .*
        \s*Initial\s+SPF\s+schedule\s+delay\s+(?P<init_spf>\d+)\s+msecs
        \s*Minimum\s+hold\s+time\s+between\s+two\s+consecutive\s+SPFs\s+(?P<min_spf>\d+)\s+msecs
        \s*Maximum\s+wait\s+time\s+between\s+two\s+consecutive\s+SPFs\s+(?P<max_spf>\d+)\s+msecs
        .*
        \s*Reference\s+bandwidth\s+unit\s+is\s+(?P<ref_bw>\d+)\s+mbps
    '''
    ospf_proc = dict()
    regex = re.compile(process_pattern, re.VERBOSE + re.DOTALL)

    match = regex.search(inf_nei)
    if match:
        ospf_proc = match.groupdict()
        ospf_proc.update({
            'is_abr': inf_nei.find('area border') != -1,
            'is_asbr': inf_nei.find('autonomous system boundary') != -1,
            'is_stub_rtr': inf_nei.find('Originating router-LSAs with max') != -1,
            'has_ispf': inf_nei.find('Incremental-SPF enabled') != -1,
            'has_bfd': inf_nei.find('BFD is enabled') != -1,
            'has_ttlsec': inf_nei.find('Strict TTL checking enabled') != -1
        })
        ospf[str(task.host)]['process'] = ospf_proc

    area_pattern = r'''
        Area\s+(?:BACKBONE\()?(?P<id>\d+)(?:\))?\s+
        Number\s+of\s+interfaces\s+in\s+this\s+area\s+is\s+(?P<num_intfs>\d+).*\n
        \s+(?:It\s+is\s+a\s+(?P<type>\w+)\s+area)?
    '''
    regex = re.compile(area_pattern, re.VERBOSE)
    if match:
        areas = [match.groupdict() for match in regex.finditer(inf_nei)]
        for area in areas:
            # area['num_intfs'] = FilterModule._try_int(area['num_intfs'])
            # area['id'] = FilterModule._try_int(area['id'])
            if not area['type']:
                area['type'] = 'standard'
            else:
                area['type'] = area['type'].lower()
        ospf[str(task.host)]['areas'] = areas
    #########################################################
    # Check command 'show ip ospf database database-summary'
    cmd = f'show ip ospf database database-summary'
    r = task.run(
        name=f'Command: {cmd}',
        task=netmiko_send_command,
        command_string=cmd
        # severity_level=logging.ERROR
    )
    res = r.result
    process_pattern = r'''
        Process\s+(?P<process_id>\d+)\s+database\s+summary\s+
        (?:LSA\s+Type\s+Count\s+Delete\s+Maxage\s+)?
        Router\s+(?P<total_lsa1>\d+).*\n\s+
        Network\s+(?P<total_lsa2>\d+).*\n\s+
        Summary\s+Net\s+(?P<total_lsa3>\d+).*\n\s+
        Summary\s+ASBR\s+(?P<total_lsa4>\d+).*\n\s+
        Type-7\s+Ext\s+(?P<total_lsa7>\d+).*
        \s+Type-5\s+Ext\s+(?P<total_lsa5>\d+)
    '''
    regex = re.compile(process_pattern, re.VERBOSE + re.DOTALL)
    match = regex.search(res)
    dbms_sum = dict()
    if match:
        match = regex.search(res)
        dbms_sum = match.groupdict()

        ospf[str(task.host)]['dbms_sum'] = dbms_sum

    area_pattern = r'''
        Area\s+(?P<id>\d+)\s+database\s+summary\s+
        (?:LSA\s+Type\s+Count\s+Delete\s+Maxage\s+)?
        Router\s+(?P<num_lsa1>\d+).*\n\s+
        Network\s+(?P<num_lsa2>\d+).*\n\s+
        Summary\s+Net\s+(?P<num_lsa3>\d+).*\n\s+
        Summary\s+ASBR\s+(?P<num_lsa4>\d+).*\n\s+
        Type-7\s+Ext\s+(?P<num_lsa7>\d+)
    '''
    regex = re.compile(area_pattern, re.VERBOSE)
    # match = regex.search(res)
    dbms_sum_areas = list()
    if match:
        dbms_sum_areas = [match.groupdict() for match in regex.finditer(res)]

        ospf[str(task.host)]['dbms_sum_areas'] = dbms_sum_areas


def configure_ospf_simple(task, dt, tmp_ospf="ospf_01"):
    task.host['ospf_networks'] = dt['ospf_config'][str(task.host)]['ospf_networks']

    if 'ospf_proc' in dt['ospf_config'][str(task.host)]:
        task.host['ospf_proc'] = dt['ospf_config'][str(task.host)]['ospf_proc']

    if 'ospf_int' in dt['ospf_config'][str(task.host)]:
        task.host['ospf_int'] = dt['ospf_config'][str(task.host)]['ospf_int']

    # print_result(task.host)
    r = task.run(
        name="Configure OSPF",
        task=template_file,
        template=f'{tmp_ospf}.j2',
        path=f'templates',
        # severity_level=logging.ERROR
    )
    config = r.result

    task.run(
        name="Loading Configuration on the device",
        task=netmiko_send_config,
        config_commands=config,
    )


def print_title_host(title_txt):
    # print(colored("="*40, 'yellow'), colored(f'{title_txt}', 'magenta', attrs=['bold']), colored("="*40, 'yellow'))
    ln = len(title_txt)
    lf = int((80-ln)/2)
    rf = int(80 - ln)
    # print("*"*lf, colored(f' {title_txt}', 'magenta', attrs=['bold', 'underline']), "*"*rf)
    print(colored(f' {title_txt}', 'magenta', attrs=['bold']))


def print_title_result(title_txt):
    # print(colored("="*35, 'yellow'), colored(f'{title_txt}', 'magenta', attrs=['bold']), colored("="*35, 'yellow'))
    ln = len(title_txt)
    lf = int((80-ln)/2)
    rf = int(80 - lf - ln)
    print("="*lf, colored(f' {title_txt}', 'green'), "="*rf)


def print_body_result(body_txt):
    print(colored(body_txt, 'white'))


if __name__ == '__main__':
    ag = check_argument_parser()
    with open("src_cfg/lab_ospf_01.yaml", mode='r') as yaml_id:
        init_data = yaml.load(yaml_id)
    # print(init_data)
    nr = InitNornir(config_file="config.yaml", dry_run=False)
    # ipdb.set_trace()
    nr.config.jinja2.filters['ipaddr'] = ipaddr
    if ag.ospf:
        res = nr.run(task=configure_ospf_simple, dt=init_data)
        print_result(res)
    elif ag.ploop:
        res = nr.run(task=ping_check_loop, dt=init_data)
        for i in res:
            print(colored(f'=============================== {i} ==================================', 'yellow'))
            for jj in res[i]:
                if re.match(".*Success\srate\sis\s0.*", str(jj), re.DOTALL):
                    print(colored(f'Task: Ping to {jj.name} failed', 'red'))
                    print(colored(f'{str(jj)}', 'green', 'on_grey'))
    elif ag.cmd:
        res = nr.run(task=run_command_vios, cmd=ag.cmd)
        # print_result(results, vars=["stdout"])
        for i in res:
            print(colored(f'=============================== {i}: {res[i][1].name} ==================================', 'white'))
            # print(colored(f'Task: {res[i][1].name}', 'white'))
            print(colored(f'{str(res[i][1])}', 'green', 'on_grey'))

    elif ag.info_ospf:

        if ag.filter:
            filter_output = ag.filter
        else:
            filter_output = ['area', 'nei', 'db']
        ospf_info = dict()
        res = nr.run(task=get_info_ospf, ospf=ospf_info)
        # print_result(res)
        for i in sorted(ospf_info):
            print(colored("*"*83, 'yellow', attrs=['bold']))
            type_host = ""

            if ospf_info[i]['process']['is_abr']:
                # ABR:{is_abr} ASBR:{is_asbr} STUB:{is_stub_rtr}
                type_host += f'ABR '
            if ospf_info[i]['process']['is_asbr']:
                type_host += f'ASBR '
            if ospf_info[i]['process']['is_stub_rtr']:
                type_host += f'STUB '
            print_title_host(f'HOSTNAME: {i}' + '   OSPFid: {id:4s} RID: {rid:15s}'.format_map(ospf_info[i]['process']) + type_host)

            # print_title_result("Process OSPF")
            # print_body_result('Process: {id:4s} RID: {rid:15s} ABR:{is_abr} ASBR:{is_asbr} STUB:{is_stub_rtr}'.format_map(ospf_info[i]['process']))
            if 'area' in filter_output:
                print_title_result("Areas")
                for n in ospf_info[i]['areas']:
                    print_body_result('Area: {id:6s} Type: {type:16s} Number of Interfaces: {num_intfs:4s} '.format_map(n))

            if 'nei' in filter_output:
                print_title_result("Neighbors")
                for n in ospf_info[i]['neighbor']:
                    print_body_result('{rid:15s} {state:6s} {role:6s} {peer:15s} {intf:s}'.format_map(n))
            if 'db' in filter_output:
                print_title_result("Database Summary")
                # print_body_result('Process: {process_id:4s}'.format_map(ospf_info[i]['dbms_sum']))
                print_body_result('Proc: {process_id:4s} LSA1: {total_lsa1:5s} LSA2: {total_lsa2:5s} LSA3: {total_lsa3:5s} LSA4: {total_lsa4:5s} LSA7: {total_lsa7:5s} LSA5: {total_lsa5:5s}'.format_map(ospf_info[i]['dbms_sum']))
                print_title_result("Area Database Summary ")
                for n in ospf_info[i]['dbms_sum_areas']:
                    # print_body_result('Area: {id:4s} '.format_map(n))
                    print_body_result('Area: {id:4s} LSA1: {num_lsa1:5s} LSA2: {num_lsa2:5s} LSA3: {num_lsa3:5s} LSA4: {num_lsa4:5s} LSA7: {num_lsa7:5s}'.format_map(n))

        # print(ospf_info['R3'])
