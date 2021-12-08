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
        # These are strings of ascii characters, each one of which is a BYTE...
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

def _binarize(arr: np.ndarray) -> np.ndarray:
    """convert {-1, 1} to {0, 1}"""
    assert arr.dtype == 'int64'
    return arr > 0

def _unbinarize(arr: np.ndarray) -> np.ndarray:
    """convert {0, 1} to {-1, 1}"""
    assert arr.dtype == 'bool'
    return arr * 2 -1

def a2b(arr: np.ndarray, binarize=False) -> str:
    """ array to bytes int """   
    if binarize:
        arr = _binarize(arr)
    return np.packbits(arr).tobytes()

def b2a(arr: bytes, size: int) -> np.ndarray:
    """decode bytes hex int object back to ndarray"""
    assert len(arr) * 8 == size
    # calculate each boolean value
    out_arr = np.zeros(size, dtype=bool)
    for i in range(size):
        N = arr[len(arr) - 1 - i//8]
        out_arr[i] = bool((N >> (i%8)) & 1)
    return _unbinarize(out_arr[::-1])

def p4_binarized_linear_layer(W: np.ndarray, b: np.ndarray, x_mat: np.ndarray):
    # assert ((W == 1) or (W == -1)).all()
    # assert ((b == 1) or (x_mat == -1)).all()
    # assert ((b == 1) or (x_mat == -1)).all()
    # TODO add activation

    # get interface & address
    iface = get_if()
    src_mac = get_if_hwaddr(iface)

    # convert to bits
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
            pkt = pkt / Perceptron(
                step_acc=0, finished=0,
                weight=a2b(W, binarize=True),
                bias=a2b(b, binarize=True),
                x=a2b(x_mat, binarize=True),
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
    return b2a(in_pkt_result.x, 16)

def main():
    # Create numpy arrays
    x = np.array([1, -1, 1, -1, 1, -1, 1, -1, 1, -1, 1, -1, 1, -1, 1, -1], dtype=int)
    # generate random W and b out of {-1, 1}
    W = np.random.rand(16, 16).round().astype(int) * 2 - 1
    b = np.random.rand(16).round().astype(int) * 2 - 1

    # Call multiplication subroutine
    x_result = p4_binarized_linear_layer(W, b, x)

    print('result from switch:', x_result)
    true_val = np.sign(W @ x + b)
    print('W @ x + b =', true_val)
    print('eq:', (x_result == true_val).sum() / len(x_result))

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
