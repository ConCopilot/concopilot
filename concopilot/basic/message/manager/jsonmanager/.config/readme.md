# basic-msg-manager

This is a Message Manager that parse a Cerebrum `InteractResponse` json string content with multiple repairing techniques, referencing the [Auto-GPT](https://github.com/Significant-Gravitas/Auto-GPT) project.

Change its `plugin_prompt_generator` config in a Copilot `config.yaml` for specific purpose.

See [`config.yaml`](./config.yaml) for details.

## Config

No custom `config` section in its `config.yaml`.

## Usage

Adding the configs below to the `config.yaml` file for a specific Copilot:

```yaml
message_manager:
  group_id: org.concopilot.basic.message.manager
  artifact_id: basic-msg-manager
  version: <version>
```
