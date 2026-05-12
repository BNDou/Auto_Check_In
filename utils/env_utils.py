#!/usr/bin/env python
# coding=utf-8
'''
FilePath     : /Auto_Check_In/utils/env_utils.py
Description  :  
Author       : BNDou
Date         : 2026-05-12 22:46:51
LastEditTime : 2026-05-12 23:11:18

utils/env_utils.py - 环境变量工具模块

提供从环境变量中读取多账号配置的功能。
'''

import os
import re


def get_env(env_name: str) -> list:
    """
    从环境变量中读取多账号配置，支持换行符和&&分隔
    
    Args:
        env_name: 环境变量名称
        
    Returns:
        list: 账号列表，如果环境变量不存在或为空则返回空列表
    """
    value = os.environ.get(env_name, '')
    if not value:
        return []
    return [item.strip() for item in re.split(r'\n|&&', value) if item.strip()]
