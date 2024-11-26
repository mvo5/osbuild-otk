import yaml

from .annotation import OtkNode, OtkDict, OtkList
from .error import (
    IncludeNotFoundError, OTKError,
    ParseError, ParseTypeError, ParseValueError, ParseDuplicatedYamlKeyError,
    TransformDirectiveTypeError, TransformDirectiveUnknownError,
)


# from https://gist.github.com/pypt/94d747fe5180851196eb?permalink_comment_id=4653474#gistcomment-4653474
# pylint: disable=too-many-ancestors
class SafeOtkLoader(yaml.SafeLoader):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, self.otk_dict_constructor)
        self.add_constructor(yaml.resolver.BaseResolver.DEFAULT_SEQUENCE_TAG, self.otk_list_constructor)
        self.add_constructor('tag:yaml.org,2002:str', self.otk_construct_yaml_str)
        self.add_constructor('tag:yaml.org,2002:int', self.otk_construct_yaml_int)

    def otk_src_from(self, node):
        line = node.start_mark.line
        # XXX: why is this needed :(
        if isinstance(node, yaml.nodes.ScalarNode):
            line += 1
        # XXX: make this a dataclass instead
        return f"{node.start_mark.name}:{line}"

    def construct_mapping(self, node, deep=False):
        mapping = set()
        # check duplicates
        for key_node, _ in node.value:
            if ':merge' in key_node.tag:
                continue
            key = self.construct_object(key_node, deep=deep)
            if key in mapping:
                if "otk." in key:
                    raise ParseDuplicatedYamlKeyError(
                        f"duplicated {key!r} key found, try using "
                        f"{key}.<uniq-tag>, e.g. {key}.foo")
                raise ParseDuplicatedYamlKeyError(f"duplicated {key!r} key found")
            mapping.add(key)
        return super().construct_mapping(node, deep)

    def otk_dict_constructor(self, loader, node):
        data = loader.construct_mapping(node)
        otk_dict = OtkDict(data)
        otk_dict.otk_src = self.otk_src_from(node)
        return otk_dict

    def otk_list_constructor(self, loader, node):
        data = loader.construct_sequence(node)
        otk_list = OtkList(data)
        otk_list.otk_src = self.otk_src_from(node)
        return otk_list

    def otk_construct_yaml_str(self, loader, node):
        data = loader.construct_scalar(node)
        otk_scalar = OtkNode(data)
        otk_scalar.otk_src = self.otk_src_from(node)
        return otk_scalar

    def otk_construct_yaml_int(self, loader, node):
        data = super().construct_yaml_int(node)
        otk_int = OtkNode(data)
        otk_int.otk_src = self.otk_src_from(node)
        return otk_int
