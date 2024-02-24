import yaml
import uuid


class YamlDumper(yaml.SafeDumper):
    pass


YamlDumper.add_representer(uuid.UUID, lambda dumper, data : dumper.represent_str(str(data)))
YamlDumper.add_multi_representer(dict, YamlDumper.represent_dict)
