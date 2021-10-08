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

# np.random.seed(42) # set seed

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
        # BitField("weight", 0, 256),                   # weight matrix (256 bits)
        # BitField("bias", 0, 16),                      # bias matrix (16 bits)
        # BitField("x", 0, 16),                         # input vector (16 bits)

        StrFixedLenField("weight", None, length=32), # weight matrix (256 bits)
        StrFixedLenField("bias", None, length=2),    # bias vector (16 bits)
        StrFixedLenField("x", None, length=2),       # input vector (16 bits)
    ] 

bind_layers(Ether, Perceptron, type=0x9999)

def print_pkt(pkt):
    pkt.show()
    print()
    pkt.show2()
    sys.stdout.flush()

def a2b(arr: np.ndarray) -> str:
    """ array to bytes int """   
    return np.packbits(arr).tobytes()

def b2a(arr: bytes, size: int) -> np.ndarray:
    """decode bytes hex int object back to ndarray"""
    assert len(arr) * 8 == size
    # calculate each boolean value
    out_arr = np.zeros(size, dtype=bool)
    for i in range(size):
        N = arr[len(arr) - 1 - i//8]
        out_arr[i] = bool((N >> (i%8)) & 1)
    return out_arr[::-1]

def main():
    # if len(sys.argv)<2:
    # print 'usage: regex.py <string>'
    # exit(1)
    iface = get_if()
    src_mac = get_if_hwaddr(iface)

    # Create numpy arrays
    W = np.identity(16, dtype=bool)
    W[0] = 1
    W[7] = 1
    x_mat = np.random.rand(16).round().astype(bool)
    b = np.array([1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0], dtype=bool)
    init_result_mat = np.zeros(16, dtype=bool)
    # convert to bits
    #pkt = pkt / Regex(current_state=state, W_num_bytes=len(W_bytes), x_num_bytes=len(x_bytes))
    step = 0
    in_pkt_result = None
    while True:
        pkt = Ether(src=src_mac, dst='ff:ff:ff:ff:ff:ff')
        # Perceptron(weight=W.tobytes(),  bias=b.tobytes(), x=x.tobytes())
        if in_pkt_result:
            # subsequent packet (reuse acc)
            pkt = pkt / in_pkt_result
        else:
            # first packet
            # print('mat lengths:', len(W.tobytes()), len(b.tobytes()), len(x_mat.tobytes()))
            pkt = pkt / Perceptron(
                step_acc=0, finished=0,
                weight=a2b(W),
                bias=a2b(b),
                x=a2b(x_mat),
            )
        print(f"[sending packet #{step}...]")
        print_pkt(pkt)
        in_pkt = srp1(pkt, iface=iface, verbose=False)
        assert len(in_pkt) == len(pkt), f"Got {len(in_pkt)} bytes back, sent {len(pkt)}"
        print(f"[received packet #{step}...]")
        print_pkt(in_pkt)
        in_pkt_result = in_pkt[Perceptron]
        # breakpoint()
        step += 1
        print(in_pkt.step_acc, '//', in_pkt_result.finished)
        if in_pkt_result.finished == 1:
            print(f"finished after step {step}!")
            break
        else:
            print(f"continuing step {step}")
    # TODO fix unpacking.
    print(in_pkt_result.x)
    x_mat_result = b2a(in_pkt_result.x, 16)
    print('result from switch:', x_mat_result)
    print('b =', b)
    print('W @ x_mat =', W @ x_mat)
    true_val = W @ x_mat + b
    print('W @ x_mat + b =', true_val)
    print('eq:', (x_mat_result == true_val))
    print('eq:', (x_mat_result == true_val).sum() / len(x_mat_result))
    print('true_eq:', (x_mat_result == True).sum() / len(x_mat_result))
    breakpoint()

def test_binary_methods():
    n = np.random.rand(16).round().astype(bool)
    print(n)
    b = a2b(n)
    print(b)
    b_hat = b2a(b, 16)
    print(b_hat)

if __name__ == '__main__':
    # test_binary_methods()
    main()
