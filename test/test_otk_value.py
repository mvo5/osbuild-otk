from otk.context import CommonContext
from otk.transform import process_include
from otk.traversal import State


TEST_YAML = """\
otk.version: 1

otk.target.osbuild:
  list:
    - 1
    - 2
  dict:
   nested_dict:
    foo: bar
    bar: baz
"""


def test_annotate(tmp_path):
    test_yaml_path = tmp_path / "test.yaml"
    test_yaml_path.write_text(TEST_YAML)

    ctx = CommonContext(target_requested="osbuild")
    state = State()
    tree = process_include(ctx, state, test_yaml_path)

    assert "test.yaml:0" in tree.otk_src
    assert "test.yaml:1" in tree["otk.version"].otk_src
    assert "test.yaml:3" in tree["otk.target.osbuild"].otk_src
    assert "test.yaml:4" in tree["otk.target.osbuild"]["list"].otk_src
    assert "test.yaml:5" in tree["otk.target.osbuild"]["list"][0].otk_src
    assert "test.yaml:6" in tree["otk.target.osbuild"]["list"][1].otk_src
    assert "test.yaml:7" in tree["otk.target.osbuild"]["dict"].otk_src
    assert "test.yaml:8" in tree["otk.target.osbuild"]["dict"]["nested_dict"].otk_src
    assert "test.yaml:9" in tree["otk.target.osbuild"]["dict"]["nested_dict"]["foo"].otk_src
    assert "test.yaml:10" in tree["otk.target.osbuild"]["dict"]["nested_dict"]["bar"].otk_src
