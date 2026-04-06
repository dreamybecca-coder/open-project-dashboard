#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
严格筛选金融投资专项
核心：量化交易、A股、美股投资
排除：泛金融、保险、贷款、支付等
"""

import json
import re

# 读取数据
with open('records_raw.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

finance_names = []

# 核心关键词（必须明确提到）
CORE_KEYWORDS = [
    '量化', '量化策略', '量化投资', '量化交易',
    'A股', '美股', '港股',
    '股票投资', '股票交易',
    '技术分析', '因子投资',
    '程序化交易', '算法交易',
]

# 排除关键词（有这些就不算）
EXCLUDE_KEYWORDS = [
    '保险', '贷款', '信贷', '支付', '理财顾问',
    '金融科技', '区块链', '数字货币', '虚拟货币',
    'NFT', '元宇宙', 'Web3',
]

for person in data:
    fields = person.get('fields', {})
    name = fields.get('姓名', '')
    
    # 项目介绍和目标
    one_page_intro = fields.get('一页纸完整介绍', '') or ''
    personal_intro = fields.get('案主个人介绍', '') or ''
    story = fields.get('一堂学习故事', '') or ''
    
    # 合并项目相关文本
    project_text = f"{one_page_intro} {personal_intro} {story}"
    
    # 排除：有排除关键词的
    if any(ex in project_text for ex in EXCLUDE_KEYWORDS):
        continue
    
    # 核心：必须提到核心关键词
    if any(kw in project_text for kw in CORE_KEYWORDS):
        finance_names.append(name)
        print(f"✅ {name}")

print(f"\n总计: {len(finance_names)}人")

# 保存
with open('strict_finance.json', 'w', encoding='utf-8') as f:
    json.dump(finance_names, f, ensure_ascii=False, indent=2)

print(f"\n已保存到 strict_finance.json")
