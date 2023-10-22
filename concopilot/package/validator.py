# -*- coding: utf-8 -*-

import logging

from typing import List, Tuple

from ..util.config.tool import read_config_file


logger=logging.getLogger('[Concopilot]')


def validate_component_config_file(file_name: str) -> Tuple[str, str, str]:
    config=read_config_file(file_name)

    if config.group_id is None or not isinstance(config.group_id, str) or config.group_id.strip()=='':
        raise ValueError('`group_id` is a necessary string field and must not be empty!')
    if config.artifact_id is None or not isinstance(config.artifact_id, str) or config.artifact_id.strip()=='':
        raise ValueError('`artifact_id` is a necessary string field and must not be empty!')
    if config.version is None or not isinstance(config.version, str) or config.version.strip()=='':
        raise ValueError('`version` is a necessary string field and must not be empty!')

    if config.type is None or not isinstance(config.type, str) or config.type.strip()=='':
        raise ValueError('`type` is a necessary string field and must not be empty!')
    if config.as_plugin is None or not isinstance(config.as_plugin, bool):
        raise ValueError('`as_plugin` is a necessary bool field and must not be empty!')

    if config.as_plugin:
        if config.info is None:
            raise ValueError('`config.info` must be provided if this component is regarded as a plugin!')
        if config.info.title is None or not isinstance(config.info.title, str) or config.info.title.strip()=='':
            raise ValueError('`config.info.title` is a necessary string field and must not be empty if this component is regarded as a plugin!')
        if (config.info.description is None or not isinstance(config.info.description, str) or config.info.description.strip()=='') and (config.info.description_for_model is None or not isinstance(config.info.description_for_model, str) or config.info.description_for_model.strip()==''):
            raise ValueError('Either `config.info.description` or `config.info.description_for_model` must exist and must not be empty if this component is regarded as a plugin!')
        if config.commands is None or not isinstance(config.commands, List) or len(config.commands)==0:
            logger.warning('`config.commands` list field represents the commands this component provided must exist and must not be empty if this component is regarded as a plugin!')

    if config.url is None or not isinstance(config.url, str) or config.url.strip()=='':
        logger.warning('A `url` string field represents the project repository is recommended.')
    if config.developers is None or not isinstance(config.developers, List) or len(config.developers)==0:
        logger.warning('A `developers` list field represents the project developers is recommended.')
    if config.licenses is None or not isinstance(config.licenses, List) or len(config.licenses)==0:
        logger.warning('A `licenses` list field represents the project licenses is recommended.')

    return config.group_id, config.artifact_id, config.version
