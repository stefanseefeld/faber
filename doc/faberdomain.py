#
# Copyright (c) 2017 Stefan Seefeld
# All rights reserved.
#
# This file is part of Faber. It is made available under the
# Boost Software License, Version 1.0.
# (Consult LICENSE or http://www.boost.org/LICENSE_1_0.txt)

from docutils.parsers.rst import Directive
from docutils.parsers.rst import directives
from docutils import nodes
from docutils.statemachine import ViewList
from sphinx.domains import Domain, ObjType, Index
from sphinx.directives import ObjectDescription
from sphinx.roles import XRefRole
from sphinx import addnodes
from sphinx.ext import graphviz


class Field(object):

    def __init__(self, name, label):
        self.name = name
        self.label = label
    
    def make_field(self, directive):
        # treat content like docfields.Field
        value = directive.options.get(self.name)
        if value:
            name = nodes.field_name('', self.label)
            para = nodes.paragraph(rawsource=value)
            content = ViewList()
            content.append(value, *directive.content.items[0])
            directive.state.nested_parse(content, directive.content_offset, para)
            body = nodes.field_body('', para)
            return nodes.field('', name, body)


class XRefField(Field):

    def __init__(self, name, label, domain):
        super(XRefField, self).__init__(name, label)
        self.domain = domain
    
    def make_xref(self, rolename, target):
        refnode = addnodes.pending_xref('',
                                        refdomain=self.domain,
                                        reftype=rolename,
                                        reftarget=target)
        refnode += addnodes.literal_emphasis(target, target)
        return refnode

    def make_field(self, directive):
        # treat content like docfields.Field
        value = directive.options.get(self.name)
        if value:
            name = nodes.field_name('', self.label)
            para = nodes.paragraph(rawsource=value)
            value = value.split(',')
            refs = [self.make_xref('', v.strip()) for v in value]
            content = [nodes.Text(',')]*(2*len(refs)-1)
            content[::2] = refs
            para += content
            body = nodes.field_body('', para)
            return nodes.field('', name, body)


class InheritanceField(Field):

    def make_field(self, directive):
        # treat content like docfields.Field
        value = directive.options.get(self.name)
        if value:
            name = nodes.field_name('', self.label)
            para = nodes.paragraph(rawsource=value)
            bases = value.split(',')
            # graph attributes
            code = ['rankdir=LR;']
            code += ['size="8.0, 12.0";']
            t = directive.arguments[0]
            # node attributes
            node_attrs = ', '.join(['shape="box"',
                                    'fontsize="10"',
                                    'height="0.25"',
                                    'fontname="Vera Sans, DejaVu Sans, Liberation Sans, Arial, Helvetica, sans"',
                                    'style="setlinewidth(0.5) filled"',
                                    'fillcolor="khaki3:khaki1"'])
            code += ['%s [%s, label="%s"];'%(t, node_attrs, t)]
            code += ['%s [%s, label="%s"];'%(b, node_attrs, b) for b in bases]
            code += ['%s -> %s;'%(t, b) for b in bases]
            node = graphviz.graphviz()
            node['code'] = 'digraph I {\n%s\n}\n'%'\n'.join(code)
            node['options'] = {}
            body = nodes.field_body('', node)        
            return nodes.field('', name, body)


class FaberDirective(ObjectDescription):
    """Inject field options into content."""

    has_content = True
    required_arguments = 1
    optional_arguments = 0
    fields = []

    def run(self):
        index, content = ObjectDescription.run(self)
        fields = nodes.field_list()
        for f in self.fields:
            field = f.make_field(self)
            if field:
                fields += field
        # Insert option fields right after signature
        content.insert(1, fields)

        name = self.arguments[0]
        module = self.options.get('module', None)
        qname = '{}.{}'.format(module, name) if module else name
        classname = self.name[4:] if self.name.startswith('fab:') else self.name
        indextext = '{} ({} in {})'.format(name, classname, module)
        index = addnodes.index(entries=[('single', indextext, name, None, None)])
        return [index, content]


class Feature(FaberDirective):
    
    option_spec = dict(module=directives.unchanged,
                       attributes=directives.unchanged,
                       values=directives.unchanged)
    fields = [Field('module', 'Defined in'),
              XRefField('attributes', 'Attributes', 'py'),
              Field('values', 'Possible values')]

    
class Action(FaberDirective):

    option_spec = dict(features=directives.unchanged,
                       module=directives.unchanged,
                       abstract=directives.unchanged)
    fields = [Field('features', 'Features used')]


class Tool(FaberDirective):
    
    option_spec = dict(module=directives.unchanged,
                       bases=directives.unchanged,
                       actions=directives.unchanged)
    fields = [Field('module', 'Defined in'),
              InheritanceField('bases', 'Inheritance'),
              Field('actions', 'Actions')]


class FaberDomain(Domain):
    """Faber domain."""

    name = 'fab'
    label = 'Faber'

    object_types = dict(feature=ObjType('feature', 'feature', 'obj'),
                        tool=ObjType('tool', 'tool', 'obj'),
                        action=ObjType('action', 'action', 'obj'))

    directives = dict(feature=Feature,
                      tool=Tool,
                      action=Action)

    roles = dict(feature=XRefRole(),
                 tool=XRefRole(),
                 action=XRefRole())

    initial_data = dict(feature={})  # path: (docname, synopsis)

    #indices = [FeatureIndex, ToolIndex]


def setup(app):

    app.add_domain(FaberDomain)
