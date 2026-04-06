#!/usr/bin/env python3
import json
import re

# 读取原始数据
with open('records_raw.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# 关键词列表（内容IP/营销自动化相关）
core_keywords = [
    '内容IP', 'IP', '营销IP', '个人IP',
    '营销自动化', '自动化营销',
    'AI营销', '人工智能营销',
    '内容自动化', '内容生产自动化',
    '自媒体矩阵', '矩阵账号',
    '内容矩阵', '账号矩阵',
    '短视频自动化', '视频自动化',
    '直播自动化',
    '内容工作流', '内容SOP',
    'AI内容', 'AI生成内容',
    '内容生产', '内容创作',
    '营销漏斗', '转化漏斗',
    '私域自动化', '私域运营',
    '流量自动化', '流量获取',
    '内容分发', '多平台分发',
    '爆款内容', '爆款公式',
    '内容变现', '知识变现',
    '精细化内容', '内容体系',
]

# 排除关键词（避免误判）
exclude_keywords = [
    '区块链', '数字货币', '虚拟货币',
    'NFT', '元宇宙', 'Web3',
    '量化', '量化策略', 'A股', '美股',  # 金融专项
    '跨境电商', '出海', '外贸',  # 出海专项
]

# 筛选结果
results = []

for person in data:
    fields = person.get('fields', {})
    name = fields.get('姓名', '')
    
    # 合并所有文本字段
    one_page_intro = fields.get('一页纸完整介绍', '') or ''
    personal_intro = fields.get('案主个人介绍', '') or ''
    story = fields.get('一堂学习故事', '') or ''
    project_goal = fields.get('航海目标和计划', '') or ''
    project_intro = fields.get('项目课题介绍', '') or ''
    
    # 合并文本
    all_text = f"{one_page_intro} {personal_intro} {story} {project_goal} {project_intro}"
    
    # 检查是否包含排除关键词
    has_exclude = False
    for kw in exclude_keywords:
        if kw in all_text:
            has_exclude = True
            break
    
    if has_exclude:
        continue
    
    # 检查是否包含核心关键词
    matched_keywords = []
    for kw in core_keywords:
        if kw in all_text:
            matched_keywords.append(kw)
    
    # 如果匹配到至少1个关键词
    if matched_keywords:
        results.append({
            'name': name,
            'id': fields.get('案主编号'),
            'matched_keywords': matched_keywords,
            'intro_preview': one_page_intro[:100] if one_page_intro else (personal_intro[:100] if personal_intro else ''),
            'project_goal': project_goal[:100],
        })

# 按匹配关键词数量排序
results.sort(key=lambda x: len(x['matched_keywords']), reverse=True)

print(f'筛选结果：共{len(results)}人')
print('=' * 80)

# 输出前30个案例
for i, r in enumerate(results[:30], 1):
    print(f'{i}. {r["name"]} (ID: {r["id"]})')
    print(f'   匹配关键词: {", ".join(r["matched_keywords"])}')
    if r["project_goal"]:
        print(f'   项目目标: {r["project_goal"]}')
    print()

# 保存结果
with open('ip_automation_names.json', 'w', encoding='utf-8') as f:
    json.dump([r['name'] for r in results], f, ensure_ascii=False, indent=2)

print(f'\n已保存{len(results)}人到 ip_automation_names.json')
