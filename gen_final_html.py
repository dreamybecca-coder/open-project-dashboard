#!/usr/bin/env python3
import json

with open('dashboard_data.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

projects = data['projects']
meta = data['meta']

all_sorted = sorted(projects, key=lambda x: -x['totalScore'])
quka_sorted = sorted([p for p in projects if '获客' in str(p['specialCategories'])], key=lambda x: -x['totalScore'])
chugai_sorted = sorted([p for p in projects if '出海' in str(p['specialCategories'])], key=lambda x: -x['totalScore'])
finance_sorted = sorted([p for p in projects if '金融投资' in str(p['specialCategories'])], key=lambda x: -x['totalScore'])

total_n = meta['total']
sp_n = meta['grade_counts'].get('S+',0) + meta['grade_counts'].get('S',0)
a_n = meta['grade_counts'].get('A',0)

# 从文件读取专项统计
with open('strict_finance.json', 'r', encoding='utf-8') as f:
    finance_names = json.load(f)
with open('ultra_strict_quka.json', 'r', encoding='utf-8') as f:
    quka_names = json.load(f)
with open('ultra_strict_chuhai.json', 'r', encoding='utf-8') as f:
    chuhai_names = json.load(f)

qk_n = len(quka_names)
cg_n = len(chuhai_names)
fi_n = len(finance_names)

css = """
* { box-sizing: border-box; margin: 0; padding: 0; }
body { font-family: -apple-system, BlinkMacSystemFont, 'PingFang SC', 'Microsoft YaHei', sans-serif; background: #0f0f1a; color: #e0e0e0; min-height: 100vh; }
.header { background: linear-gradient(135deg, #1a1a2e, #16213e); padding: 18px 32px; border-bottom: 1px solid #2d2d44; display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 12px; }
.header h1 { font-size: 20px; color: #fff; }
.header .subtitle { font-size: 12px; color: #888; margin-top: 4px; }
.header-stats { display: flex; gap: 16px; flex-wrap: wrap; }
.hstat { text-align: center; }
.hstat .n { font-size: 22px; font-weight: bold; }
.hstat .l { font-size: 11px; color: #888; }
.tabs { display: flex; background: #1a1a2e; border-bottom: 1px solid #2d2d44; overflow-x: auto; }
.tab { padding: 14px 24px; cursor: pointer; font-size: 14px; color: #888; border-bottom: 3px solid transparent; white-space: nowrap; transition: all 0.2s; }
.tab:hover { color: #ccc; }
.tab.active { color: #fff; border-bottom-color: #4a9eff; }
.tab .badge { display: inline-block; background: rgba(255,255,255,0.1); color: #aaa; border-radius: 10px; padding: 1px 7px; font-size: 11px; margin-left: 6px; }
.tab.active .badge { background: rgba(74,158,255,0.2); color: #4a9eff; }
.content { padding: 20px 32px; }
.toolbar { display: flex; gap: 12px; margin-bottom: 16px; flex-wrap: wrap; align-items: center; }
.search-input { flex: 1; min-width: 200px; background: #252540; border: 1px solid #3a3a5c; border-radius: 8px; padding: 8px 14px; color: #e0e0e0; font-size: 14px; outline: none; }
.search-input:focus { border-color: #4a9eff; }
.filter-select { background: #252540; border: 1px solid #3a3a5c; border-radius: 8px; padding: 8px 12px; color: #e0e0e0; font-size: 13px; outline: none; cursor: pointer; }
.result-count { font-size: 13px; color: #888; padding: 8px 0; }
.cards-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(330px, 1fr)); gap: 16px; }
.card { background: #1e1e30; border: 1px solid #2d2d44; border-radius: 12px; padding: 16px; cursor: pointer; transition: all 0.2s; position: relative; }
.card:hover { border-color: #4a9eff; transform: translateY(-2px); box-shadow: 0 8px 24px rgba(74,158,255,0.15); }
.card-top { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 10px; }
.card-name { font-size: 16px; font-weight: bold; color: #fff; }
.card-region { font-size: 11px; color: #888; margin-top: 2px; }
.card-score-block { text-align: right; }
.card-total { font-size: 28px; font-weight: bold; line-height: 1; }
.card-grade { display: inline-block; font-size: 11px; padding: 2px 8px; border-radius: 10px; margin-top: 3px; font-weight: bold; }
.score-bars { margin: 10px 0; }
.bar-row { display: flex; align-items: center; gap: 8px; margin-bottom: 5px; font-size: 11px; }
.bar-label { width: 72px; color: #888; flex-shrink: 0; }
.bar-track { flex: 1; background: #2d2d44; border-radius: 3px; height: 6px; overflow: hidden; }
.bar-fill { height: 100%; border-radius: 3px; }
.bar-val { width: 28px; text-align: right; color: #ccc; }
.card-tags { display: flex; flex-wrap: wrap; gap: 5px; margin-top: 8px; }
.tag { font-size: 10px; padding: 2px 8px; border-radius: 10px; background: rgba(255,255,255,0.06); color: #aaa; }
.tag.quka { background: rgba(76,175,80,0.15); color: #81C784; }
.tag.chugai { background: rgba(33,150,243,0.15); color: #64B5F6; }
.tag.finance { background: rgba(255,193,7,0.15); color: #FFD54F; }
.card-intro { font-size: 12px; color: #888; margin-top: 8px; line-height: 1.5; overflow: hidden; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; }
.rank-badge { position: absolute; top: 12px; left: -2px; background: linear-gradient(135deg, #4a9eff, #7c4dff); color: #fff; font-size: 11px; font-weight: bold; padding: 2px 10px 2px 8px; border-radius: 0 10px 10px 0; }
.modal-overlay { display: none; position: fixed; inset: 0; background: rgba(0,0,0,0.7); z-index: 1000; overflow-y: auto; padding: 20px; }
.modal-overlay.show { display: flex; align-items: flex-start; justify-content: center; }
.modal { background: #1e1e30; border: 1px solid #3a3a5c; border-radius: 16px; max-width: 700px; width: 100%; padding: 28px; position: relative; margin: auto; }
.modal-close { position: absolute; top: 16px; right: 16px; background: rgba(255,255,255,0.1); border: none; color: #fff; width: 30px; height: 30px; border-radius: 50%; cursor: pointer; font-size: 16px; display: flex; align-items: center; justify-content: center; }
.modal-close:hover { background: rgba(255,255,255,0.2); }
.modal-title { font-size: 22px; font-weight: bold; color: #fff; margin-bottom: 4px; }
.modal-meta { font-size: 13px; color: #888; margin-bottom: 16px; }
.score-section { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; margin-bottom: 20px; }
.score-panel { background: rgba(255,255,255,0.03); border: 1px solid #2d2d44; border-radius: 10px; padding: 14px; }
.score-panel-title { font-size: 12px; color: #888; margin-bottom: 10px; }
.score-panel-total { font-size: 32px; font-weight: bold; margin-bottom: 10px; }
.score-item { display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px; }
.score-item-label { font-size: 12px; color: #aaa; }
.score-item-bar { flex: 1; margin: 0 10px; background: #2d2d44; border-radius: 3px; height: 5px; overflow: hidden; }
.score-item-fill { height: 100%; border-radius: 3px; }
.score-item-val { font-size: 12px; color: #e0e0e0; width: 30px; text-align: right; }
.modal-section { margin-bottom: 16px; }
.modal-section-title { font-size: 13px; font-weight: bold; color: #4a9eff; margin-bottom: 6px; }
.modal-section-content { font-size: 13px; color: #ccc; line-height: 1.7; white-space: pre-wrap; word-break: break-word; }
.special-tags { display: flex; gap: 8px; margin: 8px 0 16px; flex-wrap: wrap; }
.special-tag { padding: 4px 12px; border-radius: 20px; font-size: 12px; font-weight: bold; }
.tab-content { display: none; }
.contact-block { background: rgba(74,158,255,0.07); border: 1px solid rgba(74,158,255,0.25); border-radius: 10px; padding: 12px 16px; margin-bottom: 16px; }
.contact-label { font-size: 12px; font-weight: bold; color: #4a9eff; margin-bottom: 8px; }
.contact-items { display: flex; flex-wrap: wrap; gap: 8px; }
.contact-item { font-size: 13px; padding: 4px 12px; border-radius: 20px; cursor: default; }
.contact-nick { background: rgba(255,255,255,0.08); color: #ccc; }
.contact-phone { background: rgba(76,175,80,0.15); color: #81C784; }
.contact-wx { background: rgba(33,150,243,0.15); color: #64B5F6; }
.contact-qrs { display: flex; flex-wrap: wrap; gap: 10px; margin-top: 10px; }
.contact-qr { width: 120px; height: 120px; object-fit: contain; border-radius: 8px; background: #fff; padding: 4px; }
.tab-content.active { display: block; }
"""

body_top = f"""
<div class="header">
  <div>
    <h1>开源案主评估系统 · 100分制</h1>
    <div class="subtitle">仅含"接受开源挑战"的案主 · 人评50分 + 项评50分</div>
  </div>
  <div class="header-stats">
    <div class="hstat"><div class="n" style="color:#4a9eff">{total_n}</div><div class="l">开源案主</div></div>
    <div class="hstat"><div class="n" style="color:#FFD700">{sp_n}</div><div class="l">S级精英</div></div>
    <div class="hstat"><div class="n" style="color:#4CAF50">{a_n}</div><div class="l">A级优先</div></div>
    <div class="hstat"><div class="n" style="color:#81C784">{qk_n}</div><div class="l">获客专项</div></div>
    <div class="hstat"><div class="n" style="color:#64B5F6">{cg_n}</div><div class="l">出海专项</div></div>
    <div class="hstat"><div class="n" style="color:#FFD54F">{fi_n}</div><div class="l">金融专项</div></div>
  </div>
</div>

<div class="tabs">
  <div class="tab active" onclick="switchTab('all')">全部总榜 <span class="badge">{total_n}</span></div>
  <div class="tab" onclick="switchTab('quka')">🎯 获客专项 <span class="badge">{qk_n}</span></div>
  <div class="tab" onclick="switchTab('chugai')">🌍 出海专项 <span class="badge">{cg_n}</span></div>
  <div class="tab" onclick="switchTab('finance')">💰 金融投资 <span class="badge">{fi_n}</span></div>
</div>

<div class="content">
  <div class="tab-content active" id="tab-all">
    <div class="toolbar">
      <input class="search-input" id="search-all" placeholder="搜索姓名、地区、简介..." oninput="filterCards('all')">
      <select class="filter-select" id="grade-all" onchange="filterCards('all')">
        <option value="">全部等级</option>
        <option value="S+">S+ 顶尖</option><option value="S">S 优秀</option>
        <option value="A">A 高潜</option><option value="B">B 良好</option><option value="C">C 普通</option>
      </select>
      <select class="filter-select" id="region-all" onchange="filterCards('all')">
        <option value="">全部地区</option>
        <option value="华北">华北</option><option value="华东">华东</option>
        <option value="华南">华南</option><option value="华中">华中</option>
        <option value="西南">西南</option><option value="西北">西北</option><option value="东北">东北</option>
      </select>
    </div>
    <div class="result-count" id="count-all"></div>
    <div class="cards-grid" id="grid-all"></div>
  </div>
  <div class="tab-content" id="tab-quka">
    <div class="toolbar">
      <input class="search-input" id="search-quka" placeholder="搜索获客专项案主..." oninput="filterCards('quka')">
      <select class="filter-select" id="grade-quka" onchange="filterCards('quka')">
        <option value="">全部等级</option>
        <option value="S+">S+</option><option value="S">S</option>
        <option value="A">A</option><option value="B">B</option>
      </select>
    </div>
    <div class="result-count" id="count-quka"></div>
    <div class="cards-grid" id="grid-quka"></div>
  </div>
  <div class="tab-content" id="tab-chugai">
    <div class="toolbar">
      <input class="search-input" id="search-chugai" placeholder="搜索出海专项案主..." oninput="filterCards('chugai')">
      <select class="filter-select" id="grade-chugai" onchange="filterCards('chugai')">
        <option value="">全部等级</option>
        <option value="S+">S+</option><option value="S">S</option>
        <option value="A">A</option><option value="B">B</option>
      </select>
    </div>
    <div class="result-count" id="count-chugai"></div>
    <div class="cards-grid" id="grid-chugai"></div>
  </div>
  <div class="tab-content" id="tab-finance">
    <div class="toolbar">
      <input class="search-input" id="search-finance" placeholder="搜索金融投资专项案主..." oninput="filterCards('finance')">
      <select class="filter-select" id="grade-finance" onchange="filterCards('finance')">
        <option value="">全部等级</option>
        <option value="S+">S+</option><option value="S">S</option>
        <option value="A">A</option><option value="B">B</option>
      </select>
    </div>
    <div class="result-count" id="count-finance"></div>
    <div class="cards-grid" id="grid-finance"></div>
  </div>
</div>
<div class="modal-overlay" id="modal" onclick="closeModal(event)">
  <div class="modal" id="modal-content"></div>
</div>
"""

js = """
const GRADE_COLOR = {'S+':'#FFD700','S':'#FFA500','A':'#4CAF50','B':'#2196F3','C':'#9C27B0','D':'#607D8B'};

function buildContactHtml(p) {
  const phones = p.phones || [];
  const wxIds = p.wechatIds || [];
  const qrs = p.qrImgs || [];
  const nick = p.wechatNick || '';
  if (!phones.length && !wxIds.length && !qrs.length && !nick) return '';
  let items = '';
  if (nick) items += '<span class="contact-item contact-nick">微信昵称: '+nick+'</span>';
  phones.forEach(ph => { items += '<span class="contact-item contact-phone">📱 '+ph+'</span>'; });
  wxIds.forEach(wx => { items += '<span class="contact-item contact-wx">💬 '+wx+'</span>'; });
  let qrHtml = qrs.map(url => '<img src="'+url+'" class="contact-qr" alt="微信二维码" onerror="this.style.display=\\'none\\'">').join('');
  return '<div class="contact-block"><div class="contact-label">📬 联系方式</div><div class="contact-items">'+items+'</div>'+(qrHtml?'<div class="contact-qrs">'+qrHtml+'</div>':'')+'</div>';
}
"""
js += "const DATA = {\n"
js += "  all: " + json.dumps(all_sorted, ensure_ascii=False) + ",\n"
js += "  quka: " + json.dumps(quka_sorted, ensure_ascii=False) + ",\n"
js += "  chugai: " + json.dumps(chugai_sorted, ensure_ascii=False) + ",\n"
js += "  finance: " + json.dumps(finance_sorted, ensure_ascii=False) + "\n};\n"

js += """
function switchTab(name) {
  const names = ['all','quka','chugai','finance'];
  document.querySelectorAll('.tab').forEach((t,i) => { t.classList.toggle('active', names[i]===name); });
  document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
  document.getElementById('tab-'+name).classList.add('active');
  filterCards(name);
}
function filterCards(tabName) {
  const query = (document.getElementById('search-'+tabName)?.value||'').toLowerCase();
  const gradeFilter = document.getElementById('grade-'+tabName)?.value||'';
  const regionFilter = tabName==='all'?(document.getElementById('region-all')?.value||''):'';
  let list = DATA[tabName];
  if (query) list = list.filter(p => p.name.toLowerCase().includes(query)||(p.region||'').includes(query)||(p.intro||'').toLowerCase().includes(query)||(p.projectIntro||'').toLowerCase().includes(query));
  if (gradeFilter) list = list.filter(p => p.grade===gradeFilter);
  if (regionFilter) list = list.filter(p => (p.region||'').includes(regionFilter));
  renderCards(tabName, list);
}
function renderCards(tabName, list) {
  const grid = document.getElementById('grid-'+tabName);
  const countEl = document.getElementById('count-'+tabName);
  countEl.textContent = '共 '+list.length+' 人';
  grid.innerHTML = list.map((p,idx) => {
    const gc = GRADE_COLOR[p.grade]||'#888';
    const cats = p.specialCategories||[];
    const tagHtml = cats.map(c => {
      const cls = c==='获客'?'quka':c==='出海'?'chugai':'finance';
      return '<span class="tag '+cls+'">'+c+'</span>';
    }).join('');
    const regType = (p.registerType||'').includes('MBA')?'🎓MBA':'一人战队';
    const intro = (p.introSummary||p.intro||'').substring(0,120);
    return '<div class="card" onclick="openModal(\\''+p.id+'\\',\\''+tabName+'\\')">'+
      '<div class="rank-badge">#'+(idx+1)+'</div>'+
      '<div class="card-top"><div><div class="card-name">'+p.name+'</div><div class="card-region">'+(p.region||'')+' · '+regType+' · 学分'+p.credits+'</div></div>'+
      '<div class="card-score-block"><div class="card-total" style="color:'+gc+'">'+p.totalScore+'</div><div class="card-grade" style="background:'+gc+'22;color:'+gc+'">'+p.grade+'</div></div></div>'+
      '<div class="score-bars">'+
        '<div class="bar-row"><span class="bar-label">人评 '+p.person_total+'</span><div class="bar-track"><div class="bar-fill" style="width:'+Math.round(p.person_total/50*100)+'%;background:#FF7043"></div></div><span class="bar-val">/50</span></div>'+
        '<div class="bar-row"><span class="bar-label">项评 '+p.project_total+'</span><div class="bar-track"><div class="bar-fill" style="width:'+Math.round(p.project_total/50*100)+'%;background:#4a9eff"></div></div><span class="bar-val">/50</span></div>'+
      '</div>'+
      (tagHtml?'<div class="card-tags">'+tagHtml+'</div>':'')+
      '<div class="card-intro">'+intro+'</div></div>';
  }).join('');
}
function openModal(id, tabName) {
  const p = DATA[tabName].find(x => x.id===id);
  if(!p) return;
  const gc = GRADE_COLOR[p.grade]||'#888';
  const rank = DATA[tabName].findIndex(x=>x.id===id)+1;
  const cats = p.specialCategories||[];
  const catColors = {'获客':'#81C784','出海':'#64B5F6','金融投资':'#FFD54F'};
  const catBgs = {'获客':'rgba(76,175,80,0.15)','出海':'rgba(33,150,243,0.15)','金融投资':'rgba(255,193,7,0.15)'};
  const specialTagHtml = cats.map(c => '<span class="special-tag" style="background:'+(catBgs[c]||'rgba(255,255,255,0.1)')+';color:'+(catColors[c]||'#ccc')+'">'+c+' 专项</span>').join('');
  const scoreRows1 = [['P1 实战经验',p.p1_experience,10,'#FF7043'],['P2 国际视野',p.p2_global,10,'#FF9800'],['P3 业务成绩',p.p3_achievements,15,'#F44336'],['P4 专业能力',p.p4_expertise,8,'#FF5722'],['P5 创业基因',p.p5_entrepreneurship,7,'#E91E63']].map(([l,v,m,c])=>'<div class="score-item"><span class="score-item-label">'+l+'</span><div class="score-item-bar"><div class="score-item-fill" style="width:'+Math.round(v/m*100)+'%;background:'+c+'"></div></div><span class="score-item-val">'+v+'/'+m+'</span></div>').join('');
  const scoreRows2 = [['D1 领域相关',p.d1_relevance,15,'#4a9eff'],['D2 项目成熟',p.d2_maturity,15,'#00BCD4'],['D3 协同价值',p.d3_synergy,10,'#009688'],['D4 学习价值',p.d4_learning,10,'#4CAF50']].map(([l,v,m,c])=>'<div class="score-item"><span class="score-item-label">'+l+'</span><div class="score-item-bar"><div class="score-item-fill" style="width:'+Math.round(v/m*100)+'%;background:'+c+'"></div></div><span class="score-item-val">'+v+'/'+m+'</span></div>').join('');
  document.getElementById('modal-content').innerHTML =
    '<button class="modal-close" onclick="document.getElementById(\\'modal\\').classList.remove(\\'show\\')">✕</button>'+
    '<div class="modal-title" style="color:'+gc+'">'+p.name+' <span style="font-size:16px;color:#888">#'+rank+'名</span></div>'+
    '<div class="modal-meta">'+(p.region||'')+' · '+(p.registerType||'')+' · 学分 '+p.credits+' · 总分 '+p.totalScore+'分('+p.grade+')</div>'+
    (specialTagHtml?'<div class="special-tags">'+specialTagHtml+'</div>':'')+
    buildContactHtml(p)+
    '<div class="score-section">'+
      '<div class="score-panel"><div class="score-panel-title">🧑 人评（满分50）</div><div class="score-panel-total" style="color:#FF7043">'+p.person_total+' <span style="font-size:14px;color:#888">/ 50</span></div>'+scoreRows1+'</div>'+
      '<div class="score-panel"><div class="score-panel-title">📁 项评（满分50）</div><div class="score-panel-total" style="color:#4a9eff">'+p.project_total+' <span style="font-size:14px;color:#888">/ 50</span></div>'+scoreRows2+'</div>'+
    '</div>'+
    (p.intro?'<div class="modal-section"><div class="modal-section-title">个人介绍</div><div class="modal-section-content">'+p.intro+'</div></div>':'')+
    (p.projectIntro?'<div class="modal-section"><div class="modal-section-title">项目介绍</div><div class="modal-section-content">'+p.projectIntro+'</div></div>':'')+
    (p.goal?'<div class="modal-section"><div class="modal-section-title">航海目标</div><div class="modal-section-content">'+p.goal+'</div></div>':'');
  document.getElementById('modal').classList.add('show');
}
function closeModal(e) { if(e.target===document.getElementById('modal')) document.getElementById('modal').classList.remove('show'); }
filterCards('all');
"""

full_html = "<!DOCTYPE html>\n<html lang=\"zh-CN\">\n<head>\n<meta charset=\"UTF-8\">\n<meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\">\n<title>开源案主评估系统 - 100分制</title>\n<style>\n" + css + "\n</style>\n</head>\n<body>\n" + body_top + "\n<script>\n" + js + "\n</script>\n</body>\n</html>"

with open('dashboard_final.html', 'w', encoding='utf-8') as f:
    f.write(full_html)

print(f"OK: dashboard_final.html ({len(full_html)//1024}KB)")
print(f"总榜:{len(all_sorted)} 获客:{len(quka_sorted)} 出海:{len(chugai_sorted)} 金融:{len(finance_sorted)}")
