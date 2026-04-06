import json
import re

# 读取数据
with open('records_raw.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# 读取评分
with open('evaluated_projects_v3.json', 'r', encoding='utf-8') as f:
    scores = json.load(f)

# 严格筛选三类项目
quka_projects = []  # 获客专项
chuhai_projects = []  # 出海专项
finance_projects = []  # 金融投资专项

for person in data:
    fields = person.get('fields', {})
    name = fields.get('姓名', '')
    intro = fields.get('案主个人介绍', '') or ''
    project_intro = fields.get('项目课题介绍', '') or fields.get('一页纸完整介绍', '') or ''
    goal = fields.get('航海目标和计划', '') or ''
    
    # 合并所有文本
    all_text = f"{intro}\n{project_intro}\n{goal}"
    
    # 获取评分
    score_data = scores.get(name, {})
    total_score = score_data.get('score', 0)
    grade = score_data.get('grade', 'N/A')
    
    # 获客专项：内容IP、内容工作流、自媒体矩阵获客、自媒体
    quka_keywords = [
        r'内容.*IP', r'IP.*内容', r'个人IP', r'知识IP',
        r'自媒体', r'公众号', r'视频号', r'抖音号', r'小红书',
        r'内容营销', r'内容创作', r'内容生产', r'内容工作流',
        r'获客.*系统', r'获客.*流程', r'流量.*获客',
        r'直播.*获客', r'短视频.*获客', r'内容.*获客',
        r'私域.*运营', r'社群.*运营.*获客',
        r'矩阵.*账号', r'多平台.*运营',
        r'AI.*内容', r'AI.*写作', r'AI.*文案',
    ]
    
    # 出海专项：跨境电商为主
    chuhai_keywords = [
        r'跨境.*电商', r'跨境电商', r'出海.*电商',
        r'Amazon|亚马逊', r'Shopee', r'速卖通', r'eBay',
        r'独立站', r'DTC', r'跨境.*店铺',
        r'海外.*市场', r'全球.*市场', r'国际化.*运营',
        r'跨境.*物流', r'海外仓',
        r'出海.*品牌', r'品牌.*出海',
        r'海外.*用户', r'全球.*用户',
    ]
    
    # 金融投资专项：AI二级市场投资策略
    finance_keywords = [
        r'二级市场', r'A股', r'港股', r'美股',
        r'量化.*投资', r'量化.*策略', r'量化.*交易',
        r'投资.*策略', r'交易.*策略',
        r'股票.*分析', r'证券.*分析',
        r'基金.*投资', r'私募.*投资',
        r'技术.*分析', r'基本面.*分析',
        r'AI.*投资', r'AI.*量化', r'AI.*选股',
        r'智能.*投顾', r'投资.*决策.*系统',
    ]
    
    # 检测获客
    is_quka = False
    quka_reason = []
    for pattern in quka_keywords:
        if re.search(pattern, all_text, re.IGNORECASE):
            is_quka = True
            quka_reason.append(pattern)
    
    # 检测出海
    is_chuhai = False
    chuhai_reason = []
    for pattern in chuhai_keywords:
        if re.search(pattern, all_text, re.IGNORECASE):
            is_chuhai = True
            chuhai_reason.append(pattern)
    
    # 检测金融
    is_finance = False
    finance_reason = []
    for pattern in finance_keywords:
        if re.search(pattern, all_text, re.IGNORECASE):
            is_finance = True
            finance_reason.append(pattern)
    
    # 添加到对应列表（一个人可以属于多个分类）
    if is_quka:
        quka_projects.append({
            'name': name,
            'score': total_score,
            'grade': grade,
            'reasons': quka_reason[:3],  # 只保留前3个匹配原因
            'intro': project_intro[:200]
        })
    
    if is_chuhai:
        chuhai_projects.append({
            'name': name,
            'score': total_score,
            'grade': grade,
            'reasons': chuhai_reason[:3],
            'intro': project_intro[:200]
        })
    
    if is_finance:
        finance_projects.append({
            'name': name,
            'score': total_score,
            'grade': grade,
            'reasons': finance_reason[:3],
            'intro': project_intro[:200]
        })

# 按分数排序
quka_projects.sort(key=lambda x: x['score'], reverse=True)
chuhai_projects.sort(key=lambda x: x['score'], reverse=True)
finance_projects.sort(key=lambda x: x['score'], reverse=True)

print(f"🎯 获客专项（内容IP、自媒体矩阵、内容工作流）：{len(quka_projects)}人")
print(f"🌍 出海专项（跨境电商为主）：{len(chuhai_projects)}人")
print(f"💰 金融投资专项（AI二级市场投资策略）：{len(finance_projects)}人")

# 保存结果
with open('strict_quka.json', 'w', encoding='utf-8') as f:
    json.dump([p['name'] for p in quka_projects], f, ensure_ascii=False, indent=2)

with open('strict_chuhai.json', 'w', encoding='utf-8') as f:
    json.dump([p['name'] for p in chuhai_projects], f, ensure_ascii=False, indent=2)

with open('strict_finance.json', 'w', encoding='utf-8') as f:
    json.dump([p['name'] for p in finance_projects], f, ensure_ascii=False, indent=2)

print("\n✓ 已保存到 strict_quka.json, strict_chuhai.json, strict_finance.json")

# 打印典型案例
print("\n" + "="*80)
print("🎯 获客专项 Top10:")
for i, p in enumerate(quka_projects[:10], 1):
    print(f"{i}. {p['name']} - {p['score']}分({p['grade']}) - 匹配: {', '.join(p['reasons'][:2])}")
    print(f"   {p['intro'][:100]}...")

print("\n" + "="*80)
print("🌍 出海专项 Top10:")
for i, p in enumerate(chuhai_projects[:10], 1):
    print(f"{i}. {p['name']} - {p['score']}分({p['grade']}) - 匹配: {', '.join(p['reasons'][:2])}")
    print(f"   {p['intro'][:100]}...")

print("\n" + "="*80)
print("💰 金融投资专项 Top10:")
for i, p in enumerate(finance_projects[:10], 1):
    print(f"{i}. {p['name']} - {p['score']}分({p['grade']}) - 匹配: {', '.join(p['reasons'][:2])}")
    print(f"   {p['intro'][:100]}...")
