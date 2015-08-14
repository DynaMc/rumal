#!/usr/bin/env python
#
# highlights.py
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston,
# MA  02111-1307  USA
#
# Author:   Tarun Kumar <reach.tarun.here@gmail.com>
#

def generate_threats(data):
    return "wrapper function for threats"

def generate_warnings(data):
    return "wrapper function for warnings"

# Threat Functions

def exploit_threats(node):
    output = []
    for exploits in node['exploits']:
        threat = {}
        threat['type'] = 'exploit'
        threat['details'] = {
        'Module' : exploit['module']
        'Description' : exploit['description']
        'CVE' : exploit['cve']
        'Additional Info' : exploit['data']
        }
        output.append(threat)
    return output

