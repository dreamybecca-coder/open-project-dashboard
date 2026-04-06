import json
import re

# 读取数据
with open('records_raw.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# 读取评分
with open('evaluated_projects_v3.json', 'r', encoding='utf-8') as f:
    scores = json.load(f)

# 更严格的筛选
quka_projects = []  # 获客专项
chuhai_projects = []  # 出海专项
finance_projects = []  # 金融投资专项

for person in data:
    fields = person.get('fields', {})
    name = fields.get('姓名', '')
    project_intro = fields.get('项目课题介绍', '') or fields.get('一页纸完整介绍', '') or ''
    goal = fields.get('航海目标和计划', '') or ''
    
    # 只看项目介绍和目标，不看个人介绍
    project_text = f"{project_intro}\n{goal}"
    
    # 获取评分
    score_data = scores.get(name, {})
    total_score = score_data.get('score', 0)
    grade = score_data.get('grade', 'N/A')
    
    # ===== 获客专项：内容IP、内容工作流、自媒体矩阵获客 =====
    # 必须明确提到：项目核心是做内容获客
    quka_strict_patterns = [
        r'内容IP', r'个人IP.*获客', r'IP.*运营',
        r'自媒体.*获客', r'自媒体矩阵', r'多平台.*账号',
        r'短视频.*获客', r'直播.*获客', r'内容.*获客',
        r'私域.*获客', r'社群.*获客',
        r'公众号.*运营', r'视频号.*运营', r'抖音.*运营', r'小红书.*运营',
        r'AI.*内容.*生产', r'AI.*写作', r'AI.*文案.*工具',
        r'内容.*工作流', r'内容.*矩阵',
    ]
    
    is_quka = False
    quka_reason = []
    for pattern in quka_strict_patterns:
        match = re.search(pattern, project_text, re.IGNORECASE)
        if match:
            # 检查上下文，确保是项目核心，而不是边缘提及
            context_start = max(0, match.start() - 50)
            context = project_text[context_start:match.end() + 50]
            
            # 排除边缘提及（如"可能涉及"、"未来考虑"等）
            if '可能' in context or '未来' in context or '考虑' in context:
                continue
            
            is_quka = True
            quka_reason.append(pattern)
    
    # ===== 出海专项：跨境电商为主 =====
    # 必须明确是跨境电商项目
    chuhai_strict_patterns = [
        r'跨境电商', r'跨境.*电商', r'Amazon|亚马逊', r'Shopee', r'速卖通', r'eBay',
        r'独立站.*运营', r'DTC.*品牌', r'出海.*电商',
        r'海外.*店铺', r'海外仓',
    ]
    
    is_chuhai = False
    chuhai_reason = []
    for pattern in chuhai_strict_patterns:
        match = re.search(pattern, project_text, re.IGNORECASE)
        if match:
            is_chuhai = True
            chuhai_reason.append(pattern)
    
    # ===== 金融投资专项：AI二级市场投资策略 =====
    # 必须明确是投资/量化/交易策略项目
    finance_strict_patterns = [
        r'量化.*投资', r'量化.*策略', r'量化交易',
        r'AI.*投资', r'AI.*量化', r'AI.*选股',
        r'二级市场.*投资', r'A股.*投资', r'港股.*投资', r'美股.*投资',
        r'投资策略.*系统', r'交易策略.*系统',
        r'智能投顾', r'投资决策.*AI',
    ]
    
    is_finance = False
    finance_reason = []
    for pattern in finance_strict_patterns:
        match = re.search(pattern, project_text, re.IGNORECASE)
        if match:
            is_finance = True
            finance_reason.append(pattern)
    
    # 添加到对应列表
    if is_quka:
        quka_projects.append({
            'name': name,
            'score': total_score,
            'grade': grade,
            'reasons': quka_reason[:3],
            'intro': project_intro[:300]
        })
    
    if is_chuhai:
        chuhai_projects.append({
            'name': name,
            'score': total_score,
            'grade': grade,
            'reasons': chuhai_reason[:3],
            'intro': project_intro[:300]
        })
    
    if is_finance:
        finance_projects.append({
            'name': name,
            'score': total_score,
            'grade': grade,
            'reasons': finance_reason[:3],
            'intro': project_intro[:300]
        })

# 按分数排序
quka_projects.sort(key=lambda x: x['score'], reverse=True)
chuhai_projects.sort(key=lambda x: x['score'], reverse=True)
finance_projects.sort(key=lambda x: x['score'], reverse=True)

print(f"🎯 获客专项（内容IP、自媒体矩阵、内容工作流）：{len(quka_projects)}人")
print(f"🌍 出海专项（跨境电商为主）：{len(chuhai_projects)}人")
print(f"💰 金融投资专项（AI二级市场投资策略）：{len(finance_projects)}人")

# 保存结果
with open('strict_quka_v2.json', 'w', encoding='utf-8') as f:
    json.dump([p['name'] for p in quka_projects], f, ensure_ascii=False, indent=2)

with open('strict_chuhai_v2.json', 'w', encoding='utf-8') as f:
    json.dump([p['name'] for p in chuhai_projects], f, ensure_ascii=False, indent=2)

with open('strict_finance_v2.json', 'w', encoding='utf-8') as f:
    json.dump([p['name'] for p in finance_projects], f, ensure_ascii=False, indent=2)

print("\n✓ 已保存")

# 打印典型案例
print("\n" + "="*80)
print("🎯 获客专项 Top10:")
for i, p in enumerate(quka_projects[:10], 1):
    print(f"{i}. {p['name']} - {p['score']}分({p['grade']})")
    print(f"   匹配: {', '.join(p['reasons'])}")
    print(f"   {p['intro'][:150]}...")

print("\n" + "="*80)
print("🌍 出海专项 Top10:")
for i, p in enumerate(chuhai_projects[:10], 1):
    print(f"{i}. {p['name']} - {p['score']}分({p['grade']})")
    print(f"   匹配: {', '.join(p['reasons'])}")
    print(f"   {p['intro'][:150]}...")

print("\n" + "="*80)
print("💰 金融投资专项 Top10:")
for i, p in enumerate(finance_projects[:10], 1):
    print(f"{i}. {p['name']} - {p['score']}分({p['grade']})")
    print(f"   匹配: {', '.join(p['reasons'])}")
    print(f"   {p['intro'][:150]}...")
