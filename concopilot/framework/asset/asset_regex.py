# -*- coding: utf-8 -*-

import re


asset_ref_url_pattern=re.compile(r'^\s*(?:<\|)?\s*(asset:/(/[^/]+?)+/?)\s*(?:\|>)?\s*$', re.RegexFlag.IGNORECASE)

asset_ref_common_embedding_pattern=re.compile(r'\s*<\|\s*(.*?)\s*\|>\s*')
asset_ref_img_markdown_embedding_pattern=re.compile(r'(!\[.*?])\(\s*(?:<\|)?\s*(.*?)\s*(?:\|>)?\s*\)')
