#include <core.p4>
#include <v1model.p4>

const bit<8> TYPE_NULL = 0x00;
const bit<16> TYPE_REGEX = 0x9999;

header ethernet_t {
    bit<48> dstAddr;
    bit<48> srcAddr;
    bit<16> etherType;
}

header regex_t {
    bit<15> current_state; // Current state of the DFA
    bit<7> string_length;  // Length of the string being matched
    bit<2> result;         // Result indicating whether string was matched 0 = no, 1 = yes, {2,3} = unknown
}

header char_t {
    bit<8> code;
}

struct metadata { }

struct headers {
    ethernet_t ethernet;
    regex_t regex;
    char_t char;
    char_t char2;
}

parser MyParser(packet_in packet, out headers hdr, inout metadata meta, inout standard_metadata_t standard_metadata) {
    state start {
        // TODO: fill in parser
        transition parse_ethernet;
    }

    state parse_ethernet {
        packet.extract(hdr.ethernet);
        transition select(hdr.ethernet.etherType) {
            TYPE_REGEX: parse_regex;
            default: accept;
        }
    }

    state parse_regex {
        packet.extract(hdr.regex);
        transition select(hdr.regex.string_length) {
            1: parse_one_char;
            default: parse_two_chars;
        }
    }

    state parse_one_char {
        packet.extract(hdr.char); // extract a single char
        transition accept;
    }

    state parse_two_chars {
        packet.extract(hdr.char); // extract a single char
        packet.extract(hdr.char2); // extract a second char
        transition accept;
    }

}

control MyVerifyChecksum(inout headers hdr, inout metadata meta) {
    apply { }
}

control MyIngress(inout headers hdr, inout metadata meta, inout standard_metadata_t standard_metadata) {
    action goto(bit<15> next_state) {
	    // TODO: fill in body of goto action
        hdr.regex.current_state = next_state; //todo(jxm) is this right?
    }

    action nop() {  
        hdr.regex.result = 2;
    }

    table delta {
        key = {
            hdr.regex.current_state : exact;
            hdr.char.code : exact;
        }
        actions = {
            goto;
            nop;
        }
        default_action = nop;
    }

    table delta2 {
        key = {
            hdr.regex.current_state : exact;
            hdr.char2.code : exact;
        }
        actions = {
            goto;
            nop;
        }
        default_action = nop;
    }

    action accept() {
	    // TODO: fill in body of accept action
        hdr.regex.result = 1;
    }

    action reject() {
	    // TODO: fill in body of reject action
        hdr.regex.result = 0;
    }

    table final {
        key = {
            hdr.regex.current_state: exact;
        }
        actions = {
            accept;
            reject;
            nop;
        }
    }

    apply {
	    // TODO: fill in code to simulate one step of DFA and return packet to host
        
        // forward back out the same port we came in
        standard_metadata.egress_spec = standard_metadata.ingress_port;
        // advance FSM once
        if(hdr.regex.string_length == 1) {
            // advance FSM twice
            delta.apply();
            hdr.regex.string_length = hdr.regex.string_length - 1;
        } else {
            delta.apply();
            delta2.apply();
            hdr.regex.string_length = hdr.regex.string_length - 2;
        }
        // use string length to determine when to apply final table
        // if(hdr.regex.string_length == 0) {
        final.apply();
        // }
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
        packet.emit(hdr.regex);
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
