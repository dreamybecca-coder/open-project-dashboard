#!/usr/bin/env python3
import json

# 读取原始数据
with open('records_raw.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# 核心关键词（内容IP/营销自动化，必须明确提到）
core_keywords = [
    '内容IP', '营销IP', '个人IP',
    '营销自动化', '自动化营销',
    'AI营销',
    '内容自动化', '内容生产自动化',
    '自媒体矩阵', '账号矩阵', '内容矩阵',
    '短视频自动化', '视频自动化',
    '直播自动化',
    '内容工作流', '内容SOP',
    'AI生成内容',
    '营销漏斗', '转化漏斗',
    '私域自动化',
    '流量自动化',
    '内容分发自动化',
    '精细化内容', '内容体系',
]

# 次级关键词（需要配合上下文判断）
secondary_keywords = [
    'IP矩阵', 'IP自动化',
    '内容工厂', '内容生产线',
    'AI内容生产',
    '自动化内容',
    '批量生产内容',
    '内容获客自动化',
    '营销获客自动化',
]

# 排除关键词
exclude_keywords = [
    '区块链', '数字货币', '虚拟货币', 'NFT', '元宇宙', 'Web3',
    '量化', '量化策略', 'A股', '美股', '港股', '股票投资',
    '跨境电商', '出海电商', '外贸电商',
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
    
    # 检查核心关键词
    matched_core = []
    for kw in core_keywords:
        if kw in all_text:
            matched_core.append(kw)
    
    # 检查次级关键词
    matched_secondary = []
    for kw in secondary_keywords:
        if kw in all_text:
            matched_secondary.append(kw)
    
    # 筛选标准：至少1个核心关键词，或至少2个次级关键词
    if len(matched_core) >= 1 or len(matched_secondary) >= 2:
        results.append({
            'name': name,
            'id': fields.get('案主编号'),
            'matched_core': matched_core,
            'matched_secondary': matched_secondary,
            'project_goal': project_goal[:200],
        })

# 按匹配关键词数量排序
results.sort(key=lambda x: (len(x['matched_core']), len(x['matched_secondary'])), reverse=True)

print(f'严格筛选结果：共{len(results)}人')
print('=' * 80)

# 输出前40个案例
for i, r in enumerate(results[:40], 1):
    print(f'{i}. {r["name"]} (ID: {r["id"]})')
    if r["matched_core"]:
        print(f'   核心关键词: {", ".join(r["matched_core"])}')
    if r["matched_secondary"]:
        print(f'   次级关键词: {", ".join(r["matched_secondary"])}')
    if r["project_goal"]:
        print(f'   项目目标: {r["project_goal"][:150]}')
    print()

# 保存结果
with open('strict_ip_automation_names.json', 'w', encoding='utf-8') as f:
    json.dump([r['name'] for r in results], f, ensure_ascii=False, indent=2)

print(f'\n已保存{len(results)}人到 strict_ip_automation_names.json')

# 单独输出Vikki的信息
print('\n' + '=' * 80)
print('Vikki的筛选情况:')
for r in results:
    if r['name'] == 'Vikki':
        print(f'  匹配的核心关键词: {r["matched_core"]}')
        print(f'  匹配的次级关键词: {r["matched_secondary"]}')
        print(f'  项目目标: {r["project_goal"]}')
        break
else:
    print('  Vikki未通过严格筛选')
