import json
import re

# 读取数据
with open('records_raw.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# 读取评分
with open('evaluated_projects_v3.json', 'r', encoding='utf-8') as f:
    scores = json.load(f)

# 更严格的筛选
quka_projects = []
chuhai_projects = []
finance_projects = []

for person in data:
    fields = person.get('fields', {})
    name = fields.get('姓名', '')
    project_intro = fields.get('项目课题介绍', '') or fields.get('一页纸完整介绍', '') or ''
    goal = fields.get('航海目标和计划', '') or ''
    
    project_text = f"{project_intro}\n{goal}"
    
    score_data = scores.get(name, {})
    total_score = score_data.get('score', 0)
    grade = score_data.get('grade', 'N/A')
    
    # ===== 获客专项 =====
    # 核心必须是：做内容IP/自媒体/内容生产工具
    quka_core_patterns = [
        (r'做.*自媒体', '做自媒体'),
        (r'运营.*公众号|公众号.*运营', '运营公众号'),
        (r'运营.*视频号|视频号.*运营', '运营视频号'),
        (r'运营.*抖音|抖音.*运营', '运营抖音'),
        (r'运营.*小红书|小红书.*运营', '运营小红书'),
        (r'自媒体矩阵', '自媒体矩阵'),
        (r'内容.*矩阵', '内容矩阵'),
        (r'多平台.*账号.*运营', '多平台账号运营'),
        (r'短视频.*获客', '短视频获客'),
        (r'直播.*获客', '直播获客'),
        (r'内容.*获客', '内容获客'),
        (r'私域.*获客', '私域获客'),
        (r'AI.*内容.*生产.*工具', 'AI内容生产工具'),
        (r'AI.*写作.*工具', 'AI写作工具'),
        (r'AI.*文案.*工具', 'AI文案工具'),
        (r'内容工作流', '内容工作流'),
        (r'打造.*个人IP', '打造个人IP'),
        (r'个人IP.*获客', '个人IP获客'),
    ]
    
    is_quka = False
    quka_reason = []
    for pattern, desc in quka_core_patterns:
        if re.search(pattern, project_text, re.IGNORECASE):
            is_quka = True
            quka_reason.append(desc)
    
    # ===== 出海专项 =====
    # 核心必须是：跨境电商项目
    chuhai_core_patterns = [
        (r'做.*跨境电商', '做跨境电商'),
        (r'跨境电商.*项目', '跨境电商项目'),
        (r'Amazon.*店铺|亚马逊.*店铺', 'Amazon店铺'),
        (r'Shopee.*店铺', 'Shopee店铺'),
        (r'速卖通.*店铺', '速卖通店铺'),
        (r'独立站.*品牌', '独立站品牌'),
        (r'DTC.*品牌', 'DTC品牌'),
        (r'出海.*电商', '出海电商'),
        (r'海外.*电商', '海外电商'),
    ]
    
    is_chuhai = False
    chuhai_reason = []
    for pattern, desc in chuhai_core_patterns:
        if re.search(pattern, project_text, re.IGNORECASE):
            is_chuhai = True
            chuhai_reason.append(desc)
    
    # ===== 金融投资专项 =====
    # 核心必须是：AI投资/量化系统
    finance_core_patterns = [
        (r'量化.*投资', '量化投资'),
        (r'量化交易', '量化交易'),
        (r'量化策略', '量化策略'),
        (r'AI.*投资', 'AI投资'),
        (r'AI.*量化', 'AI量化'),
        (r'AI.*选股', 'AI选股'),
        (r'智能投顾', '智能投顾'),
        (r'投资决策.*AI', '投资决策AI'),
        (r'交易策略.*AI', '交易策略AI'),
        (r'二级市场.*投资', '二级市场投资'),
        (r'股票.*AI', '股票AI'),
    ]
    
    is_finance = False
    finance_reason = []
    for pattern, desc in finance_core_patterns:
        if re.search(pattern, project_text, re.IGNORECASE):
            is_finance = True
            finance_reason.append(desc)
    
    # 添加到对应列表
    if is_quka:
        quka_projects.append({
            'name': name,
            'score': total_score,
            'grade': grade,
            'reasons': list(set(quka_reason))[:3],
            'intro': project_intro[:300]
        })
    
    if is_chuhai:
        chuhai_projects.append({
            'name': name,
            'score': total_score,
            'grade': grade,
            'reasons': list(set(chuhai_reason))[:3],
            'intro': project_intro[:300]
        })
    
    if is_finance:
        finance_projects.append({
            'name': name,
            'score': total_score,
            'grade': grade,
            'reasons': list(set(finance_reason))[:3],
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
with open('ultra_strict_quka.json', 'w', encoding='utf-8') as f:
    json.dump([p['name'] for p in quka_projects], f, ensure_ascii=False, indent=2)

with open('ultra_strict_chuhai.json', 'w', encoding='utf-8') as f:
    json.dump([p['name'] for p in chuhai_projects], f, ensure_ascii=False, indent=2)

with open('ultra_strict_finance.json', 'w', encoding='utf-8') as f:
    json.dump([p['name'] for p in finance_projects], f, ensure_ascii=False, indent=2)

print("\n✓ 已保存")

# 打印所有案例
print("\n" + "="*80)
print("🎯 获客专项全部名单:")
for i, p in enumerate(quka_projects, 1):
    print(f"{i}. {p['name']} - {p['score']}分({p['grade']}) - {', '.join(p['reasons'])}")
    print(f"   {p['intro'][:120]}...")

print("\n" + "="*80)
print("🌍 出海专项全部名单:")
for i, p in enumerate(chuhai_projects, 1):
    print(f"{i}. {p['name']} - {p['score']}分({p['grade']}) - {', '.join(p['reasons'])}")
    print(f"   {p['intro'][:120]}...")

print("\n" + "="*80)
print("💰 金融投资专项全部名单:")
for i, p in enumerate(finance_projects, 1):
    print(f"{i}. {p['name']} - {p['score']}分({p['grade']}) - {', '.join(p['reasons'])}")
    print(f"   {p['intro'][:120]}...")
