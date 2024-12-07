# -*- coding: utf-8 -*-
import yaml
def get_yaml_value(variable_name, file_path='config.yaml'):
    """
    从指定的 YAML 文件中读取变量的值。

    :param variable_name: 要读取的变量名
    :param file_path: YAML 文件的路径
    :return: 变量的值，如果变量不存在则返回 None
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            config = yaml.safe_load(file)  # 读取 YAML 文件
            return config.get(variable_name)  # 返回指定变量的值
    except Exception as e:
        print(f"读取配置文件时出错: {e}")
        return None