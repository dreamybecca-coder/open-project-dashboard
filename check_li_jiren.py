#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""检查李姬韧的详细信息"""

import json
import re

def main():
    # 读取数据
    with open('records_raw.json', 'r', encoding='utf-8') as f:
        raw_data = json.load(f)
    
    for person in raw_data:
        fields = person.get('fields', {})
        name = fields.get('姓名', '')
        intro = fields.get('案主个人介绍', '')
        
        if name == '李姬韧':
            print("姓名:", name)
            print("\n个人介绍:")
            print(intro)
            print("\n" + "="*50)
            
            # 测试各种年龄提取模式
            print("\n测试年龄提取:")
            
            # 1. 从"XX年前回国"推断
            return_match = re.search(r'(\d{1,2})\s*年前.*?(?:回国|退学回国)', intro)
            if return_match:
                years_ago = int(return_match.group(1))
                print(f"✓ 找到'{return_match.group(0)}'")
                print(f"  推断年龄: 25 + {years_ago} = {25 + years_ago}岁")
            else:
                print("✗ 未找到'XX年前回国'模式")
            
            # 2. 检查是否有"上海交大+南加州大学"
            if '南加州大学' in intro or 'USC' in intro:
                print("✓ 有海外大学背景: 南加州大学")
            
            # 3. 检查工作经验
            exp_match = re.search(r'(\d{1,2})\s*年\s*(?:经验|工作|从业)', intro)
            if exp_match:
                print(f"  工作经验: {exp_match.group(0)}")

if __name__ == '__main__':
    main()
