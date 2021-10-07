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

import numpy as np

def get_if():
    ifs=get_if_list()
    iface=None
    for i in get_if_list():
        if "eth0" in i:
            iface=i
            break;
    if not iface:
        print "Cannot find eth0 interface"
        exit(1)
    return iface

class Regex(Packet):
   fields_desc = [ BitField("current_state", 0, 15),
                   BitField("string_length", 0, 7),
                   BitField("result", 3, 2) ]

class Perceptron(Packet):
   fields_desc = [ BitField("current_state", 0, 15),
                   BitField("W_num_bytes", 0, 7), 
                   BitField("x_num_bytes", 0, 7),
   ]

bind_layers(Ether, Regex, type=0x9999)

def print_pkt(pkt):
    pkt.show2()
    sys.stdout.flush()
    
def main():
    if len(sys.argv)<2:
        print 'usage: regex.py <string>'
        exit(1)
    iface = get_if()
    src_mac = get_if_hwaddr(iface)
    W = np.array([[1, 0, 0], [0, 1, 0], [0, 0, 1]], dtype=np.float32)
    W_bytes = W.tobytes()
    x = np.array([[1], [1], [1]], dtype=np.float32) * 3
    x_bytes = x.tobytes()
    while(True):
        pkt = Ether(src=src_mac, dst='ff:ff:ff:ff:ff:ff')
        pkt = pkt / Regex(current_state=state, W_num_bytes=len(W_bytes), x_num_bytes=len(x_bytes))
        pkt = pkt / Raw(load=W_bytes)
        pkt = pkt / Raw(load=x_bytes)
        print "[sending packet...]"
        print_pkt(pkt)
        pkt = srp1(pkt, iface=iface, verbose=False)
        state = pkt[Regex].current_state
        bits = pkt[Regex].string_length
        message = pkt[Raw].load
        if not bits:
            if pkt[Regex].result == 1:
                print "[accept!]"
            elif pkt[Regex].result == 0:
                print "[reject!]"
            else:
                print "[unknown]"
            break
        
if __name__ == '__main__':
    main()
