#include <core.p4>
#include <v1model.p4>

const bit<8> TYPE_NULL = 0x00;
const bit<16> TYPE_PERCEPTRON = 0x9999;

header ethernet_t {
    bit<48> dstAddr;
    bit<48> srcAddr;
    bit<16> etherType;
}

header perceptron_t {
    bit<256> weight;        // Weight matrix of linear layer
    bit<16> bias;           // Bias vector of linear layer
    bit<16> x;              // input & output vector
}

struct metadata { }

struct headers {
    ethernet_t ethernet;
    perceptron_t perceptron;
}

parser MyParser(packet_in packet, out headers hdr, inout metadata meta, inout standard_metadata_t standard_metadata) {
    state start {
        // TODO: fill in parser
        transition parse_ethernet;
    }

    state parse_ethernet {
        packet.extract(hdr.ethernet);
        transition select(hdr.ethernet.etherType) {
            TYPE_PERCEPTRON: parse_perceptron;
            default: accept;
        }
    }

    state parse_perceptron {
        packet.extract(hdr.perceptron);
    }
}

control MyVerifyChecksum(inout headers hdr, inout metadata meta) {
    apply { }
}

control MyIngress(inout headers hdr, inout metadata meta, inout standard_metadata_t standard_metadata) {
    apply {
        // TODO multiply and add, perceptron stuff here, plus activation func!
        
        // forward back out the same port
        standard_metadata.egress_spec = standard_metadata.ingress_port;
    }
}

control MyEgress(inout headers hdr, inout metadata meta, inout standard_metadata_t standard_metadata) {
    apply { }
}

control MyComputeChecksum(inout headers hdr, inout metadata meta) {
    apply { }
}

control MyDeparser(packet_out packet, in headers hdr) {
    apply {
	    // TODO: fill in code to deparse packet
        // Don't put hdr.char back here - aka don't do: packet.emit(hdr.char);
        packet.emit(hdr.ethernet);
        packet.emit(hdr.perceptron);
    }
}

V1Switch(
  MyParser(),
  MyVerifyChecksum(),
  MyIngress(),
  MyEgress(),
  MyComputeChecksum(),
  MyDeparser()
) main;
