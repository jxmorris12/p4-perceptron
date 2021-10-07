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

# class Regex(Packet):
#    fields_desc = [ BitField("current_state", 0, 15),
#                    BitField("string_length", 0, 7),
#                    BitField("result", 3, 2) ]

class Perceptron(Packet):
  fields_desc = [ BitField("weight", 0, 256),
                   BitField("bias", 0, 16), 
                   BitField("input", 0, 16),
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

    # Create numpy arrays
    W = np.identity(16, dtype=bool)
    x = np.random.rand(16).round().astype(bool)
    b = np.array([1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0], dtype=bool)
    # convert to bits
    W = W.tobytes()
    x = w.tobytes()
    b = b.tobytes()

    pkt = Ether(src=src_mac, dst='ff:ff:ff:ff:ff:ff')
    #pkt = pkt / Regex(current_state=state, W_num_bytes=len(W_bytes), x_num_bytes=len(x_bytes))
    pkt = pkt / Perceptron(weight=W, bias=b, input=x)
    print "[sending packet...]"
    print_pkt(pkt)
    pkt = srp1(pkt, iface=iface, verbose=False)
    pkt_result = pkt[Perceptron].output
    
    print('Result:', pkt_result)
    print('np result:', W @ x + b)
        
if __name__ == '__main__':
    main()
