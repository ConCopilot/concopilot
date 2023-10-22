You will be provided a YAML configuration of a Plugin. 
Your task is to summarize the configuration as precise and concise as possible, better less than 200 words.

The summarization must include these information:

1. A precise and concise "Summary" that describe the function and purpose of the Plugin.
2. A list of API descriptions for APIs that the plugin provided, also including the function and purpose of each API.

The summarization you made will be provided to some other LLM like you to help that LLM understand all the APIs provided by the Plugin, and when and how to call each API.
The YAML configuration will also be provided to the LLM, so do not provide a too detailed summarization, just provide information that can help the LLM understand the YAML configuration. 
You must make sure if you are provided the summarization and YAML configuration, you can definitely understand when and how to use the plugin in any arbitrary task.

Below is an example of the YAML configuration format:

```yaml
id: <id> # the id of the plugin
name: <name> # the name of the plugin

info:
  title: <title> # the title of the plugin
  description: <description> # description of the plugin
  description_for_human: <description_for_human> # optional, description for human to read
  description_for_model: <description_for_model> # optional, description for you and the other LLM to read
  prompt: <optional_prompt> # if exists, it is the instruction provided by the plugin auther, and you should reference carefully to it
  prompt_file_path: <optional_prompt_file_path> # you should ignore this if exists
commands: # API list that the plugin provided
  -
    command_name: <command_name_1> # the name of the first API
    description: <command_description_1> # the API description, pay more attention on this.
    parameters: # parameters that the API need to be passed.
      -
        name: <param_name_1> # the name of the first parameter
        type: string # the type of the first parameter
        description: <description_1> # the parameter description, pay more attention on this.
        enum: # entire possible values of this parameter, optional 
          - <enum_1>
          - <enum_2>
        required: true # if true, the parameter must be provided when calling the API, and if false, the parameter is optional.
        example: <example> # an optional field gives an example of the parameter.
      -
        name: <param_name_2>
        type: string
        description: <description_2>
        required: true
        example: <example>
    response: # fields in the API response
      -
        name: <response_field_name_1> # the name of the first response field
        type: string # the type of the first response field
        description: <response_field_description_1> # the response field description, pay more attention on this.
        optional: false # if false, this response field will always be included in the response, and if true, this response field can be absent in the response.
        example: <response_field_example_1> # an optional field gives an example of this response field.
      -
        name: <response_field_name_2>
        type: string
        description: <response_field_description_2>
        optional: false
        example: <response_field_example_2>
  -
    command_name: <command_name_2>
    description: <command_description_2>
    parameters: 
      # ...
    response:
      # ...
  # ...
```

Note that both the parameters and response will be a python dict (or json) respectively when calling any API.

Below is the YAML configuration that need you to summarize:
