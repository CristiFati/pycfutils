import enum
import pathlib
import sys
import traceback

import gi
import networkx
import yaml

from .registry_access import RegistryAccess

gi.require_version("Gst", "1.0")
from gi.repository import GObject, Gst

PARAMFLAG_WRITABLE = int(GObject.ParamFlags.WRITABLE)

DEFAULT_ELEMENT_INDENT = "  "
DEFAULT_PROPERTY_INDENT = "    "
DEFAULT_GSTLAUNCH = "gst-launch-1.0 -ev"
ALL_MARKER = "*"


class PipelineParser:
    _SHELL_CHARACTERS = ("(", ")", " ", ";")

    class Direction(enum.IntEnum):
        Unlinked = 0
        LeftRight = 1
        RightLeft = 2

    def __init__(self):
        self._element_classes = ()
        self._capsfilter_class = None
        try:
            p = pathlib.Path(__file__).absolute()
            p = p.parent.parent / "config" / p.stem / "property_filter.yaml"
            with open(str(p)) as f:
                self._discard_properties = yaml.safe_load(f)
        except Exception:
            traceback.print_exc()
            self._discard_properties = None

    @classmethod
    def _pad_internal(cls, pad):
        last = None
        cur = pad
        while cur and isinstance(cur, Gst.ProxyPad):
            last = cur
            cur = last.get_internal()
            if cur == pad:
                break
        return last

    @classmethod
    def _is_linked_pads(cls, pad0, pad1, direct_only=False):
        peer0 = pad0.peer
        peer1 = pad1.peer
        d = 0
        if d:
            print("_is_linked_pads:", pad0.name, pad1.name)
            print("parents:", pad0.parent.name, pad1.parent.name)
            # print(pad0.__class__.__name__, pad1.__class__.__name__)
            print(
                "peers:",
                peer0.name,
                peer1.name,
                peer0.__class__.__name__,
                peer1.__class__.__name__,
                peer0,
                peer1,
            )
            print("p:", pad0, pad1)
            # print("targets:", getattr(pad0, "get_target", None),
            #       getattr(pad1, "get_target", None))
            # print(pad0.get_target(), pad1.get_target())
        ret = peer0 == pad1 and peer1 == pad0
        if direct_only or ret:
            return ret
        int0 = cls._pad_internal(peer0)
        int1 = cls._pad_internal(peer1)
        if d:
            if int0 and int1:
                print("------ ips:", int0.name, int1.name, int0, int1)
        return int0 and int1 and int0.peer == int1 and int1.peer == int0

    @classmethod
    def element_direction(cls, gol, gor):
        for sink_pad in gol.sinkpads:
            for src_pad in gor.srcpads:
                if cls._is_linked_pads(src_pad, sink_pad):
                    return cls.Direction.RightLeft
        for sink_pad in gor.sinkpads:
            for src_pad in gol.srcpads:
                if cls._is_linked_pads(src_pad, sink_pad):
                    return cls.Direction.LeftRight
        return cls.Direction.Unlinked

    @classmethod
    def _shell_quote_item(cls, s):
        if not isinstance(s, str):
            return s
        if (s.startswith('"') and s.endswith('"')) or (
            s.startswith("'") and s.endswith("'")
        ):
            return s
        if not any(e in s for e in cls._SHELL_CHARACTERS):
            return s
        return f'"{s}"'

    @classmethod
    def _format_value(cls, val):
        return cls._shell_quote_item(str(val))

    @classmethod
    def _value(cls, val):
        if isinstance(val, int):
            ret = int(val)
        else:
            to_string = getattr(val, "to_string", None)
            if to_string:
                ret = val.to_string()
            else:
                ret = val
        return ret

    @classmethod
    def _properties(
        cls,
        go,
        discard,
        exclude_name_func=lambda arg: len(arg.sinkpads) <= 1 and len(arg.srcpads) <= 1,
    ):
        print("_properties:", go.get_factory().name)
        discard_props = (
            set(discard.get(go.get_factory().name, []) + discard.get(ALL_MARKER, []))
            if discard
            else set()
        )
        if ALL_MARKER in discard_props:
            return {}
        ret = {}
        for prop in go.list_properties():
            if prop.name in discard_props:
                continue
            if not (prop.flags & PARAMFLAG_WRITABLE):
                continue
            if prop.name == "name" and exclude_name_func(go):
                continue
            try:
                val = go.get_property(prop.name)
            except Exception:
                traceback.print_exc()
                continue
            val = cls._value(val)
            if val is None:
                continue
            if val != prop.default_value:
                ret[prop.name] = val
        return ret

    @classmethod
    def _source_reference(cls, go, level, base_indent):
        ret = [f"{base_indent * level}{go.name}. \\"]
        return ret

    @classmethod
    def _sink_reference(cls, go, level, base_indent, pad_idx):
        ret = [f"{base_indent * level}! {go.name}.{go.sinkpads[pad_idx].name} \\"]
        return ret

    def _initialize_classes(self):
        if not self._element_classes or not self._capsfilter_class:
            ra = RegistryAccess()
            self._element_classes = ra.element_classes()
            self._capsfilter_class = ra.element_classes_dict().get("capsfilter")

    def _flatten_object(self, obj, out):
        # print(f"_flatten_object: {obj}")
        if isinstance(obj, self._element_classes):
            # print(1234)
            out.append(obj)
            return
        children = getattr(obj, "children", None)
        # print(f"_flatten_object: {children}")
        if children:
            self._flatten_seq(children, out)
        else:
            out.append(obj)

    def _flatten_seq(self, seq, out):
        # print(f"_flatten_seq: {seq}")
        for obj in seq:
            self._flatten_object(obj, out)

    def _flatten(self, obj):
        self._initialize_classes()
        ret = []
        if isinstance(obj, (list, tuple)):
            self._flatten_seq(obj, ret)
        elif isinstance(obj, Gst.Object):
            self._flatten_object(obj, ret)
        else:
            print(f"Illegal object: {obj}")
        return ret

    def _generate_graph(self, obj):
        # print("_generate_graph")
        self._initialize_classes()
        ret = networkx.DiGraph()
        elements = self._flatten(obj)
        # print("_generate_graph:", len(elements))
        for item0 in elements:
            for item1 in elements:
                if item0 == item1:
                    continue
                order = self.element_direction(item0, item1)
                if order == self.Direction.LeftRight:
                    ret.add_edge(item0, item1)
                elif order == self.Direction.RightLeft:
                    ret.add_edge(item1, item0)
        return ret

    def is_capsfilter(self, element):
        if self._capsfilter_class:
            return isinstance(element, self._capsfilter_class)
        else:  # Fallback (lame)
            return element.__class__.__name__ == "GstCapsFilter"

    def _format_element(
        self, go, level, base_indent, prop_indent, discard_props, pre_link
    ):
        print("_format_element:", go.name)
        indent = base_indent * level
        link_symbol = f"{'! ' if pre_link else ''}"
        if self.is_capsfilter(go):
            # print("_format_element0")
            return [
                f"{indent}{link_symbol}"
                f"{self._shell_quote_item(go.get_property('caps').to_string())} \\"
            ]
        pindent = indent + prop_indent
        ret = [f"{indent}{link_symbol}{go.get_factory().name} \\"]
        # print("_format_element000")
        for k, v in self._properties(go, discard_props).items():
            ret.append(f"{pindent}{k}={self._format_value(v)} \\")
        print("_format_element1")
        return ret

    def _format_node(
        self,
        node,
        graph,
        level,
        base_elem_indent,
        prop_indent,
        discard_props,
        pre_link,
        multisinks,
    ):
        # print("_format_node:", node.name)
        ret = []
        levels = []
        preds = tuple(graph.predecessors(node))
        if len(preds) > 1:
            multisinks.setdefault(node, []).append(level)
            levels = multisinks[node]
            if len(levels) < len(preds):
                ret += self._sink_reference(
                    node, level, base_elem_indent, len(levels) - 1
                )
        else:
            ret += self._format_element(
                node, level, base_elem_indent, prop_indent, discard_props, pre_link
            )
            succs = tuple(graph.successors(node))
            if len(succs) > 1:
                for succ in succs:
                    ret += self._source_reference(node, level, base_elem_indent)
                    ret += self._format_node(
                        succ,
                        graph,
                        level + 1,
                        base_elem_indent,
                        prop_indent,
                        discard_props,
                        True,
                        multisinks,
                    )
            elif len(succs) == 1:
                ret += self._format_node(
                    succs[0],
                    graph,
                    level,
                    base_elem_indent,
                    prop_indent,
                    discard_props,
                    True,
                    multisinks,
                )
        if 1 < len(preds) == len(levels):
            ret += self._format_element(
                node, min(levels), base_elem_indent, prop_indent, discard_props, False
            )
        return ret

    def gst_launch(
        self,
        gst_object_root,
        level=0,
        element_indent=DEFAULT_ELEMENT_INDENT,
        property_indent=DEFAULT_PROPERTY_INDENT,
        discard_properties=None,
        command=DEFAULT_GSTLAUNCH,
    ):
        graph = self._generate_graph(gst_object_root)
        print("gst_launch:", graph, dir(graph))
        print(self._discard_properties)
        if 0:
            print("nodes", graph.nodes)
            print("edges", graph.edges)
            print("indeg", graph.in_degree)
            print("odeg", graph.out_degree)
        ret = [f"\n{command} \\"] if command else []
        srcs = [e[0] for e in graph.in_degree if e[1] == 0]
        print("gst_launch:", srcs)
        for src in srcs:
            ret += self._format_node(
                src,
                graph,
                level,
                element_indent,
                property_indent,
                (
                    self._discard_properties
                    if discard_properties is None
                    else discard_properties
                ),
                False,
                {},
            )
        print("xxxxxxxxxxxxxxxx")
        return "\n".join(ret).rstrip(" \\")


if __name__ == "__main__":
    print("This module is not meant to be run directly.\n")
    sys.exit(-1)
