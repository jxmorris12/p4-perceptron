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
        # Weird gotcha: the BitField bit counts have to accumulate to a multiple of 8,
        # so they can form full bytes.
        BitField("step_acc", 0, 7),                   # step accumulator (Max of 17 steps)
        BitField("finished", 0, 1),                   # Boolean that should flip when the computation finishes
        StrFixedLenField("weight", None, length=256), # weight matrix (256 bytes)
        StrFixedLenField("bias", None, length=16),    # bias vector (16 bytes)
        StrFixedLenField("x", None, length=16),       # input vector (16 bytes) - also scratchpad
    ] 

bind_layers(Ether, Perceptron, type=0x9999)

def print_pkt(pkt):
    # pkt.show()
    # print()
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
    #pkt = pkt / Regex(current_state=state, W_num_bytes=len(W_bytes), x_num_bytes=len(x_bytes))
    step = 0
    in_pkt_result = None
    while True:
        pkt = Ether(src=src_mac, dst='ff:ff:ff:ff:ff:ff')
        # Perceptron(weight=W.tobytes(),  bias=b.tobytes(), x=x.tobytes())
        if in_pkt_result:
            # subsequent packet (reuse acc)
            pkt = pkt / Perceptron(
                weight=W.tobytes(), bias=b.tobytes(), x=x_mat.tobytes(),
                step_acc=in_pkt_result.step_acc, finished=0
            )
        else:
            # first packet
            # print('mat lengths:', len(W.tobytes()), len(b.tobytes()), len(x_mat.tobytes()))
            pkt = pkt / Perceptron(
                step_acc=0, finished=0,
                weight=W.tobytes(), bias=b.tobytes(),
                x=x_mat.tobytes(),
            )
        print(f"[sending packet #{step}...]")
        # print_pkt(pkt)
        in_pkt = srp1(pkt, iface=iface, verbose=False)
        assert len(in_pkt) == len(pkt), f"Got {len(in_pkt)} bytes back, sent {len(pkt)}"
        print_pkt(in_pkt)
        in_pkt_result = in_pkt[Perceptron]
        # breakpoint()
        # TODO can I pass this through without parsing it to an nparray?
        x_mat = np.array([bool(bit) for bit in in_pkt_result.x], dtype=bool)

        step += 1
        print(in_pkt.step_acc, '//', in_pkt_result.finished)
        if in_pkt_result.finished == 1:
            print(f"finished at step {step}!")
            break
        else:
            print(f"continuing step {step}")
    print('result from switch:', x_mat)
    print('np result:', W @ x_mat + b)
        
if __name__ == '__main__':
    main()
