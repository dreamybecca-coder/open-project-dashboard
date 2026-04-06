#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
最终筛选：从6个年轻人中筛选出有真实海外留学背景的人
"""
import json
import re

def check_overseas(text):
    """检查是否有真实的海外留学背景"""
    text = text.replace('\n', ' ')
    
    # 1. 检查是否有明确的国家/地区或海外学校
    countries_or_schools = [
        '美国', '英国', '日本', '韩国', '新加坡', '澳大利亚', '澳洲', '加拿大',
        '德国', '法国', '意大利', '荷兰', '瑞士', '香港', '澳门', '台湾',
        '新西兰', '爱尔兰', '西班牙', '俄罗斯', '印尼', '马来西亚', '泰国',
        '早稻田', '哈佛', '牛津', '剑桥', '斯坦福', 'MIT', '麻省理工',
        '南加州大学', '哥伦比亚', '纽约大学', 'NYU', 'UCLA', '伯克利',
        '帝国理工', '伦敦大学', 'UCL', 'LSE', '爱丁堡', '曼彻斯特',
        '东京大学', '京都大学', '首尔大学', '国立大学', 'NUS',
        '墨尔本大学', '悉尼大学', '多伦多大学', '麦吉尔'
    ]
    
    found_locations = []
    for loc in countries_or_schools:
        if loc in text:
            found_locations.append(loc)
    
    if not found_locations:
        return (False, "未提到海外国家/地区或知名学校")
    
    # 2. 检查是否有留学相关描述
    study_patterns = [
        r'留学',
        r'海外.*?(?:学习|读书|攻读|就读)',
        r'毕业于.*?(?:大学|学院)',
        r'(?:学士|硕士|博士).*?(?:学位|毕业于)',
        r'本科.*?(?:毕业|就读)',
    ]
    
    has_study = False
    for pattern in study_patterns:
        if re.search(pattern, text):
            has_study = True
            break
    
    if not has_study:
        return (False, f"提到地点 {found_locations[:2]}，但无留学描述")
    
    # 3. 排除：只是业务涉及海外，但本人没有留学经历
    # 例如："做俄罗斯的中文教育"、"聚焦印尼市场"
    business_only_patterns = [
        r'做.*?的.*?教育',
        r'聚焦.*?市场',
        r'跨境.*?业务',
        r'服务.*?客户',
    ]
    
    for pattern in business_only_patterns:
        match = re.search(pattern, text)
        if match and len(found_locations) == 1:
            # 如果只有一个地点，且是业务相关，可能是误判
            return (False, f"可能只是业务涉及海外：{match.group(0)}")
    
    return (True, f"国家/学校：{', '.join(found_locations[:3])}")

# 读取数据
with open('records_raw.json', 'r', encoding='utf-8') as f:
    raw_data = json.load(f)

# 6个候选人
candidates = [
    ('赵海森', 19, '明确年龄'),
    ('秦君', 21, '大学生'),
    ('庞鑫龙', 25, '明确年龄'),
    ('杜洪芳', 26, '博士生'),
    ('李颖', 28, '明确年龄'),
    ('王一', 32, '明确年龄'),
]

print("检查6个候选人的海外留学背景：\n")

results = []

for name, age, age_source in candidates:
    # 找到对应的人
    for person in raw_data:
        fields = person.get('fields', {})
        person_name = fields.get('姓名', '')
        intro = fields.get('案主个人介绍', '')
        
        if person_name == name:
            is_overseas, reason = check_overseas(intro)
            
            status = "✓ 通过" if is_overseas else "✗ 排除"
            print(f"{name} ({age}岁): {status}")
            print(f"  理由：{reason}")
            print(f"  简介：{intro[:150]}...")
            print()
            
            if is_overseas:
                results.append({
                    'name': name,
                    'age': age,
                    'age_source': age_source,
                    'overseas_reason': reason,
                    'intro': intro
                })
            break

print(f"\n最终筛选结果：{len(results)} 人")
for i, p in enumerate(results, 1):
    print(f"{i}. {p['name']} - {p['age']}岁")
    print(f"   海外背景：{p['overseas_reason']}")
