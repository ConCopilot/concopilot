# disk

This is a Resource providing a local disk accessing, including file reading, writing, and deleting.

See [`config.yaml`](./config.yaml) for details.

## Config

1. `root_directory`: the root directory that this resource can access.
   It will check to not modify files out of this directory.

## Usage

Adding the component information under the `resource_manager.resources` section of a specific Copilot:

```yaml
resource_manager:
  # ...
  resources: # adding necessary resources for the specific Copilot
    -
      group_id: org.concopilot.basic.resource.category
      artifact_id: disk
      version: <version>
```

