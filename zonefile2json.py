"""Convert DNS zonefile to JSON"""

import os
import sys
import argparse
import json
import dns.zone
import dns.rdataclass
import dns.rdatatype


def rdata_to_dict(name, rdata: dns.rdata.Rdata, ttl=None) -> dict:
    rdclass = dns.rdataclass.to_text(rdata.rdclass)
    rdtype = dns.rdatatype.to_text(rdata.rdtype)
    ret = {
        'name': str(name),
        'class': rdclass,
        'type': rdtype,
        'rrdatas': str(rdata)
    }
    if ttl is not None:
        ret['ttl'] = ttl
    return ret


def by_rdatas(zone: dns.zone.Zone):
    rrs = []
    for (name, ttl, rdata) in zone.iterate_rdatas():
        rrs.append(rdata_to_dict(name, rdata, ttl))
    return rrs


def by_rdataset(zone: dns.zone.Zone):
    rrs = {}
    for (name, rdataset) in zone.iterate_rdatasets():
        rdname = str(name)
        rdclass = dns.rdataclass.to_text(rdataset.rdclass)
        rdtype = dns.rdatatype.to_text(rdataset.rdtype)
        ttl = rdataset.ttl
        if not rdname in rrs:
            rrs[rdname] = {}
        if not rdclass in rrs[rdname]:
            rrs[rdname][rdclass] = {}
        if not rdtype in rrs[rdname][rdclass]:
            rrs[rdname][rdclass][rdtype] = { 'ttl': ttl, 'rrdatas': [] }
        for rdata in rdataset:
            rrs[rdname][rdclass][rdtype]['rrdatas'].append(str(rdata))
    return rrs


def main():
    """Main function"""

    parser = argparse.ArgumentParser(description='Convert DNS zonefile to JSON')

    parser.add_argument('--mode',
                        dest='mode',
                        metavar='mode',
                        help='Output mode',
                        choices=['dict', 'list'],
                        default='list')
    parser.add_argument('zonefile',
                        metavar='filename',
                        nargs='?',
                        help='Input file')

    args = parser.parse_args()

    if args.zonefile:
        input = args.zonefile
    else:
        input = sys.stdin
    zone = dns.zone.from_file(input, relativize=False)
    
    if args.mode == 'dict':
        data = by_rdataset(zone)

    if args.mode == 'list':
        data = by_rdatas(zone)

    print(json.dumps(data, indent=4))


if __name__ == "__main__":
    main()
