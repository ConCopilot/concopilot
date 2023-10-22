# basic-plugin-manager

This is a general purposed Plugin Manager providing plugin indexing, retrieving, and plugin prompt generation.

It is generally not necessary to change this in a Copilot because it contains general logics only.
Change its `plugin_prompt_generator` config in a Copilot `config.yaml` for specific purpose.

See [`config.yaml`](./config.yaml) for details.

## Config

No custom `config` section in its `config.yaml`.

## Usage

Adding the configs below to the `config.yaml` file for a specific Copilot:

```yaml
plugin_manager:
  group_id: org.concopilot.basic.plugin.manager
  artifact_id: basic-plugin-manager
  version: <version>
  plugin_prompt_generator: # config its plugin_prompt_generator
    group_id: <plugin_prompt_generator_group_id>
    artifact_id: <plugin_prompt_generator_artifact_id>
    version: <plugin_prompt_generator_version>
  plugins: # adding necessary plugins for the specific Copilot
    -
      group_id: <plugin_group_id>
      artifact_id: <plugin_artifact_id>
      version: <plugin_version>
```
