#include <core.p4>
#include <v1model.p4>

const bit<16> TYPE_PERCEPTRON = 0x9999;

header ethernet_t {
    bit<48> dstAddr;
    bit<48> srcAddr;
    bit<16> etherType;
}

header perceptron_t { 
    bit<7> step_acc;          // Accumulator (step counter) - used to loop in p4 prog
    bit<1> finished;          // Starts at 0, set to 1 when looping ends
    bit<256> weight;          // Weight matrix of linear layer
    bit<16> bias;             // Bias vector of linear layer
    bit<16> x;                // input & output vector
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
        transition accept;
    }
}

control MyVerifyChecksum(inout headers hdr, inout metadata meta) {
    apply { }
}

bit<16> _g256(in bit<256> x, in bit<16> idx) {
    /** get a single bit from a bit<256> **/
    return (bit<16>)((x >> idx) & 1);
}

bit<16> _g16(in bit<16> x, in bit<4> idx) {
    /** get a single bit from a bit<16> **/
    return (bit<16>)((x >> idx) & 1);
}

control MyIngress(inout headers hdr, inout metadata meta, inout standard_metadata_t standard_metadata) {
    // Note this is shared between calls, but every cell is overwritten of the course
    // of the 16 steps. So the switch can't handle multiple concurrent computations or
    // everything will overlap and break. But we don't need to reset the scratchpad at
    // the beginning either.
    register<bit<1>>(16) scratchpad;

    apply {
        if(hdr.perceptron.step_acc < 16) {
            bit<16> j = ((bit<16>)hdr.perceptron.step_acc) * 16;
            // a single row from MLP computation (W @ x.T) + b
            bit<1> result = (bit<1>)((
                  _g256(hdr.perceptron.weight, j + 00) * _g16(hdr.perceptron.x, 00)
                + _g256(hdr.perceptron.weight, j + 01) * _g16(hdr.perceptron.x, 01)
                + _g256(hdr.perceptron.weight, j + 02) * _g16(hdr.perceptron.x, 02)
                + _g256(hdr.perceptron.weight, j + 03) * _g16(hdr.perceptron.x, 03)
                + _g256(hdr.perceptron.weight, j + 04) * _g16(hdr.perceptron.x, 04)
                + _g256(hdr.perceptron.weight, j + 05) * _g16(hdr.perceptron.x, 05)
                + _g256(hdr.perceptron.weight, j + 06) * _g16(hdr.perceptron.x, 06)
                + _g256(hdr.perceptron.weight, j + 07) * _g16(hdr.perceptron.x, 07)
                + _g256(hdr.perceptron.weight, j + 08) * _g16(hdr.perceptron.x, 08)
                + _g256(hdr.perceptron.weight, j + 09) * _g16(hdr.perceptron.x, 09)
                + _g256(hdr.perceptron.weight, j + 10) * _g16(hdr.perceptron.x, 10)
                + _g256(hdr.perceptron.weight, j + 11) * _g16(hdr.perceptron.x, 11)
                + _g256(hdr.perceptron.weight, j + 12) * _g16(hdr.perceptron.x, 12)
                + _g256(hdr.perceptron.weight, j + 13) * _g16(hdr.perceptron.x, 13)
                + _g256(hdr.perceptron.weight, j + 14) * _g16(hdr.perceptron.x, 14)
                + _g256(hdr.perceptron.weight, j + 15) * _g16(hdr.perceptron.x, 15)
            ) > 0);
            // bit<1> o = 1;
            // bit<1> z = 0;
            // WHY DOES 1+1 = False in p4??!
            // Well, to make up for it I need to do casting and add this > 0 check, which is 
            // quite inconvenient.
            // bit<1> result = (bit<1>)((
            //     o + o
            // ) > 0); // THIS IS 0!! (Unlike the numpy boolean arithmetic)

            // Store in the register
            scratchpad.write((bit<32>)hdr.perceptron.step_acc, result);
        }
        else {
            // 
            // Overwrite x with contents of the scratchpad.
            // 
            hdr.perceptron.x = 0;
            bit<1> r;
            scratchpad.read(r, 0);
            r = (bit<1>)(((bit<16>)r + _g16(hdr.perceptron.bias, 00)) > 0);
            hdr.perceptron.x = hdr.perceptron.x + ((bit<16>)r << 0);
            scratchpad.read(r, 1);
            r = (bit<1>)(((bit<16>)r + _g16(hdr.perceptron.bias, 01)) > 0);
            hdr.perceptron.x = hdr.perceptron.x + ((bit<16>)r << 1);
            scratchpad.read(r, 2);
            r = (bit<1>)(((bit<16>)r + _g16(hdr.perceptron.bias, 02)) > 0);
            hdr.perceptron.x = hdr.perceptron.x + ((bit<16>)r << 2);
            scratchpad.read(r, 3);
            r = (bit<1>)(((bit<16>)r + _g16(hdr.perceptron.bias, 03)) > 0);
            hdr.perceptron.x = hdr.perceptron.x + ((bit<16>)r << 3);
            scratchpad.read(r, 4);
            r = (bit<1>)(((bit<16>)r + _g16(hdr.perceptron.bias, 04)) > 0);
            hdr.perceptron.x = hdr.perceptron.x + ((bit<16>)r << 4);
            scratchpad.read(r, 5);
            r = (bit<1>)(((bit<16>)r + _g16(hdr.perceptron.bias, 05)) > 0);
            hdr.perceptron.x = hdr.perceptron.x + ((bit<16>)r << 5);
            scratchpad.read(r, 6);
            r = (bit<1>)(((bit<16>)r + _g16(hdr.perceptron.bias, 06)) > 0);
            hdr.perceptron.x = hdr.perceptron.x + ((bit<16>)r << 6);
            scratchpad.read(r, 7);
            r = (bit<1>)(((bit<16>)r + _g16(hdr.perceptron.bias, 07)) > 0);
            hdr.perceptron.x = hdr.perceptron.x + ((bit<16>)r << 7);
            scratchpad.read(r, 8);
            r = (bit<1>)(((bit<16>)r + _g16(hdr.perceptron.bias, 08)) > 0);
            hdr.perceptron.x = hdr.perceptron.x + ((bit<16>)r << 8);
            scratchpad.read(r, 9);
            r = (bit<1>)(((bit<16>)r + _g16(hdr.perceptron.bias, 09)) > 0);
            hdr.perceptron.x = hdr.perceptron.x + ((bit<16>)r << 9);
            scratchpad.read(r, 10);
            r = (bit<1>)(((bit<16>)r + _g16(hdr.perceptron.bias, 10)) > 0);
            hdr.perceptron.x = hdr.perceptron.x + ((bit<16>)r << 10);
            scratchpad.read(r, 11);
            r = (bit<1>)(((bit<16>)r + _g16(hdr.perceptron.bias, 11)) > 0);
            hdr.perceptron.x = hdr.perceptron.x + ((bit<16>)r << 11);
            scratchpad.read(r, 12);
            r = (bit<1>)(((bit<16>)r + _g16(hdr.perceptron.bias, 12)) > 0);
            hdr.perceptron.x = hdr.perceptron.x + ((bit<16>)r << 12);
            scratchpad.read(r, 13);
            r = (bit<1>)(((bit<16>)r + _g16(hdr.perceptron.bias, 13)) > 0);
            hdr.perceptron.x = hdr.perceptron.x + ((bit<16>)r << 13);
            scratchpad.read(r, 14);
            r = (bit<1>)(((bit<16>)r + _g16(hdr.perceptron.bias, 14)) > 0);
            hdr.perceptron.x = hdr.perceptron.x + ((bit<16>)r << 14);
            scratchpad.read(r, 15);
            r = (bit<1>)(((bit<16>)r + _g16(hdr.perceptron.bias, 15)) > 0);
            hdr.perceptron.x = hdr.perceptron.x + ((bit<16>)r << 15);

            // <g256_tests>
            // bit<256> thirteen = 13;
            // hdr.perceptron.x = (bit<16>)_g256(thirteen, 3); // should be 1
            // hdr.perceptron.x = (bit<16>)_g256(thirteen, 4); // should be 0
            // hdr.perceptron.x = (bit<16>)_g256(thirteen, 3) << 4; // should be 16
            // </g256_tests>

            // <g16_tests>
            bit<16> thirteen = 13;
            // hdr.perceptron.x = (bit<16>)_g16(thirteen, 3); // should be 1
            // hdr.perceptron.x = (bit<16>)_g16(thirteen, 4); // should be 0
            // hdr.perceptron.x = (bit<16>)_g16(thirteen, 3) << 4; // should be 16
            // hdr.perceptron.x = (bit<16>)_g16(hdr.perceptron.bias, 3); // should be 1
            // hdr.perceptron.x = (bit<16>)_g16(hdr.perceptron.bias, 4); // should be 0
            // hdr.perceptron.x = (bit<16>)_g16(hdr.perceptron.bias, 15); // should be 1
            // hdr.perceptron.x = (bit<16>)(
                    // (_g16(hdr.perceptron.bias, 00) << 0)
                // +   (_g16(hdr.perceptron.bias, 01) << 1)
                //    ((bit<16>)_g16(hdr.perceptron.bias, 01) << 1)
            // );
            // </g16_tests>

            // 
            // TODO apply activation func and/or batchnorm here?
            // 
            // Set finished bit!
            hdr.perceptron.finished = 1;
        }

        // update counters
        hdr.perceptron.step_acc = hdr.perceptron.step_acc + 1;

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
