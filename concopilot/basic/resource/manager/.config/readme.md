# basic-resource-manager

This is a general purposed Resource Manager providing resource management and resource initialization and finalization.

It is generally not necessary to change this in a Copilot because it contains general logics only.

See [`config.yaml`](./config.yaml) for details.

## Config

No custom `config` section in its `config.yaml`.

## Usage

Adding the configs below to the `config.yaml` file for a specific Copilot:

```yaml
resource_manager:
  group_id: org.concopilot.basic.resource.manager
  artifact_id: basic-resource-manager
  version: <version>
  resources: # adding necessary resources for the specific Copilot
    -
      group_id: <resource_group_id>
      artifact_id: <resource_artifact_id>
      version: <resource_version>
```
