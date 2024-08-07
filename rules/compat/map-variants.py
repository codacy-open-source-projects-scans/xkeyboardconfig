#!/usr/bin/env python3

import argparse
import re
import sys


class Layout(object):
    PATTERN = re.compile(r"(?P<layout>[^(]+)\((?P<variant>[^)]+)\)")

    def __init__(self, layout, variant=None):
        if match := self.PATTERN.match(layout):
            assert variant is None
            # parse a layout(variant) string
            layout = match.group("layout")
            variant = match.group("variant")
        self.layout = layout
        self.variant = variant

    def __str__(self):
        if self.variant:
            return "{}({})".format(self.layout, self.variant)
        else:
            return "{}".format(self.layout)


def read_file(path):
    """Returns a list of two-layout tuples [(layout1, layout2), ...]"""

    layouts = []
    for line in open(path):
        # Remove optional comment
        line = line.split("//")[0]
        # Split on whitespaces
        groups = tuple(line.split())
        length = len(groups)
        if length == 2:
            l1 = Layout(groups[0])
            l2 = Layout(groups[1])
        elif length == 4:
            l1 = Layout(groups[0], groups[1])
            l2 = Layout(groups[2], groups[3])
        else:
            raise ValueError(f"Invalid line: {line}")
        layouts.append((l1, l2))
    return layouts


# ml_s
def write_fixed_layout(dest, mappings, write_header):
    if write_header:
        dest.write("! model		layout				=	symbols\n")
    for l1, l2 in mappings:
        if l1.variant:
            raise ValueError(f"Unexpected variant: {l1}")
        dest.write("  *		{}			=	pc+{}\n".format(l1, l2))


# mln_s
def write_layout_n(dest, mappings, number, write_header):
    if write_header:
        dest.write("! model		layout[{}]	=	symbols\n".format(number))

    # symbols is one of
    #   +layout(variant):2 ... where the map-to-layout has a proper variant
    #   +layout%(v[2]):2 ... where the map-to-layout does not have a variant
    # and where the number is 1, we have a base and drop the suffix, i.e.
    # the above becomes
    #   pc+layout(variant)
    #   pc+layout%(v[1])

    base = "pc" if number == 1 else ""
    suffix = "" if number == 1 else ":{}".format(number)

    for l1, l2 in mappings:
        if l1.variant:
            raise ValueError(f"Unexpected variant: {l1}")
        second_layout = (
            str(l2) if l2.variant else "{}%(v[{}])".format(l2.layout, number)
        )
        dest.write(
            "  *		{}		=	{}+{}{}\n".format(
                l1, base, second_layout, suffix
            )
        )


# mlv_s
def write_fixed_layout_variant(dest, mappings, write_header):
    if write_header:
        dest.write("! model		layout		variant		=	symbols\n")
    for l1, l2 in mappings:
        if not l1.variant:
            raise ValueError(f"Expected variant: {l1}")
        dest.write(
            "  *		{}		{}		=	pc+{}\n".format(
                l1.layout, l1.variant, l2
            )
        )


# mlnvn_s
def write_layout_n_variant_n(dest, mappings, number, write_header):
    if write_header:
        dest.write(
            "! model		layout[{}]	variant[{}]	=	symbols\n".format(
                number, number
            )
        )

    # symbols is
    #   +layout(variant):2
    # and where the number is 1, we have a base and drop the suffix, i.e.
    # the above becomes
    #   pc+layout(variant)
    # This part is only executed for the variantMappings.lst

    base = "pc" if number == 1 else ""
    suffix = "" if number == 1 else ":{}".format(number)

    for l1, l2 in mappings:
        if not l1.variant:
            raise ValueError(f"Expected variant: {l1}")
        second_layout = (
            str(l2) if l2.variant else "{}%(v[{}])".format(l2.layout, number)
        )
        dest.write(
            "  *		{}		{}	=	{}+{}{}\n".format(
                l1.layout, l1.variant, base, second_layout, suffix
            )
        )


def map_variant(dest, files, want="mls", number=None):
    if number == 0:
        number = None

    for idx, f in enumerate(files):
        write_header = idx == 0

        mappings = read_file(f)
        if want == "mls":
            if number is None:
                write_fixed_layout(dest, mappings, write_header)
            else:
                write_layout_n(dest, mappings, number, write_header)
        elif want == "mlvs":
            if number is None:
                write_fixed_layout_variant(dest, mappings, write_header)
            else:
                write_layout_n_variant_n(dest, mappings, number, write_header)
        else:
            raise NotImplementedError()


if __name__ == "__main__":
    parser = argparse.ArgumentParser("variant mapping script")
    parser.add_argument("--want", type=str, choices=["mls", "mlvs"])
    parser.add_argument("--number", type=int, default=None)

    parser.add_argument("dest", type=str)
    parser.add_argument("files", nargs="+", type=str)
    ns = parser.parse_args()

    dest = None
    if ns.dest == "-":
        dest = sys.stdout

    with dest or open(ns.dest, "w") as fd:
        map_variant(fd, ns.files, ns.want, ns.number)
