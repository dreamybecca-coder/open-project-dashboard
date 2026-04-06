#!/usr/bin/env python3
"""
获取飞书多维表格数据并导出为Excel
"""

import json
import subprocess
import time

def run_lark_cli(command):
    """运行lark-cli命令"""
    result = subprocess.run(
        command,
        shell=True,
        capture_output=True,
        text=True
    )
    if result.returncode != 0:
        print(f"Error: {result.stderr}")
        return None
    return json.loads(result.stdout)

def get_all_records(base_token, table_id):
    """获取所有记录"""
    all_records = []
    page_token = ""
    
    while True:
        if page_token:
            cmd = f'''lark-cli api GET "/open-apis/bitable/v1/apps/{base_token}/tables/{table_id}/records" --params '{{"limit": 100, "page_token": "{page_token}"}}' 2>&1'''
        else:
            cmd = f'''lark-cli api GET "/open-apis/bitable/v1/apps/{base_token}/tables/{table_id}/records" --params '{{"limit": 100}}' 2>&1'''
        
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"Error fetching records: {result.stderr}")
            break
        
        try:
            data = json.loads(result.stdout)
            if data.get("code") == 0:
                items = data.get("data", {}).get("items", [])
                all_records.extend(items)
                print(f"Fetched {len(items)} records, total so far: {len(all_records)}")
                
                # 检查是否有更多页
                has_more = data.get("data", {}).get("has_more", False)
                page_token = data.get("data", {}).get("page_token", "")
                
                if not has_more or not page_token:
                    break
                
                time.sleep(0.3)  # 避免请求过快
            else:
                print(f"API Error: {data.get('msg')}")
                break
        except json.JSONDecodeError as e:
            print(f"JSON parse error: {e}")
            break
    
    return all_records

if __name__ == "__main__":
    BASE_TOKEN = "YTvVbnKYgaUz57sGPojcpmFDnbb"
    TABLE_ID = "tblEaOSSkv0EIJCF"
    
    print("Starting to fetch all records...")
    records = get_all_records(BASE_TOKEN, TABLE_ID)
    print(f"\nTotal records fetched: {len(records)}")
    
    # 保存为JSON备用
    with open("records_raw.json", "w", encoding="utf-8") as f:
        json.dump(records, f, ensure_ascii=False, indent=2)
    print("Raw data saved to records_raw.json")
