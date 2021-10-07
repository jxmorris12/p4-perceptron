#!/usr/bin/env python
import argparse
import sys
import socket
import random
import struct

from scapy.all import srp1, get_if_list, get_if_hwaddr, bind_layers
from scapy.all import Packet, Ether, Raw
from scapy.fields import *
import readline

# For some reason these aren't appearing in 
# my PYTHONPATH when I run through mininet,
# so I'm adding them manually so that I can 
# import numpy from my pip packages folder.
sys.path.append(
    '/home/mininet/.local/lib/python3.8/site-packages')
sys.path.append('/usr/lib/python3/dist-packages')


import numpy as np

def get_if():
    ifs=get_if_list()
    iface=None
    for i in get_if_list():
        if "eth0" in i:
            iface=i
            break;
    if not iface:
        print ("Cannot find eth0 interface")
        exit(1)
    return iface

class Perceptron(Packet):
    fields_desc = [ 
        StrFixedLenField("weight", None, length=256), # 256 bytes
        StrFixedLenField("bias", None, length=16),   # 16 bytes
        StrFixedLenField("x", None, length=16),      # 16 bytes
    ]

bind_layers(Ether, Perceptron, type=0x9999)

def print_pkt(pkt):
    pkt.show2()
    sys.stdout.flush()
    
def main():
    # if len(sys.argv)<2:
    # print 'usage: regex.py <string>'
    # exit(1)
    iface = get_if()
    src_mac = get_if_hwaddr(iface)

    # Create numpy arrays
    W = np.identity(16, dtype=bool)
    x_mat = np.random.rand(16).round().astype(bool)
    b = np.array([1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0], dtype=bool)
    # convert to bits

    pkt = Ether(src=src_mac, dst='ff:ff:ff:ff:ff:ff')
    #pkt = pkt / Regex(current_state=state, W_num_bytes=len(W_bytes), x_num_bytes=len(x_bytes))

    # Perceptron(weight=W.tobytes(),  bias=b.tobytes(), x=x.tobytes())
    pkt = pkt / Perceptron(weight=W.tobytes(), bias=b.tobytes(), x=x_mat.tobytes())
    print("[sending packet...]")
    print_pkt(pkt)
    pkt = srp1(pkt, iface=iface, verbose=False)
    # pkt_result = pkt[Perceptron].x
    pkt_result = np.array([bool(bit) for bit in pkt[Perceptron].x], dtype=bool)
    
    print('result from switch:', pkt_result)
    print('np result:', W @ x_mat + b)
        
if __name__ == '__main__':
    main()
