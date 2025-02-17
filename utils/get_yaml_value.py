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

def adjust_font_scale_add(operation, file_path='config.yaml'):
    # 读取 YAML 文件
    with open(file_path, 'r', encoding='utf-8') as file:
        data = yaml.safe_load(file)

    # 获取当前的 font_scale_add 值
    current_value = data.get('font_scale_add', 0)

    # 根据操作调整值
    if operation == 'add':
        new_value = current_value + 0.05
    elif operation == 'subtract':
        new_value = current_value - 0.05
    else:
        raise ValueError("Operation must be 'add' or 'subtract'")

    # 更新数据
    data['font_scale_add'] = round(new_value, 2)

    # 写回 YAML 文件
    with open(file_path, 'w', encoding='utf-8') as file:
        yaml.safe_dump(data, file, allow_unicode=True)

    print(f"font_scale_add updated to: {new_value}")

# # 使用示例
# adjust_font_scale_add('config.yaml', 'add')  # 增加 0.05
# adjust_font_scale_add('config.yaml', 'subtract')  # 减少 0.05
def update_font_scale(self, operation):
    new_value = adjust_font_scale_add('config.yaml', operation)
    self.update_text_box(new_value)

def update_text_box(self, value=None):
    if value is None:
        with open('config.yaml', 'r', encoding='utf-8') as file:
            data = yaml.safe_load(file)
            value = data.get('font_scale_add', 0)
    self.text_box.setText(f"当前字体倍数: {value:.2f}")