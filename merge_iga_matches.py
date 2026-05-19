import json
import glob
import os

# 文件夹路径
folder_path = "./data/iga_swiatek_previous_matches"
# 输出文件（保存到同一文件夹）
output_file = os.path.join(folder_path, "combined_matches_wta_only.json")

all_events = []

# 获取所有 page_*.json 并按页码排序
file_pattern = os.path.join(folder_path, "page_*.json")
files = glob.glob(file_pattern)
files.sort(key=lambda x: int(x.split('_')[-1].split('.')[0]))

def keep_match(match):
    """返回 True 表示保留该比赛，False 表示过滤掉"""
    # 1. 过滤双打：检查 tournament.name 是否包含 "Doubles"
    tournament = match.get('tournament')
    if tournament and isinstance(tournament, dict):
        tourn_name = tournament.get('name', '')
        if 'Doubles' in tourn_name:
            return False
    
    # 2. 只保留 WTA 赛事：检查 tournament.uniqueTournament.category.name == "WTA"
    unique_tourn = tournament.get('uniqueTournament') if tournament else None
    if unique_tourn and isinstance(unique_tourn, dict):
        category = unique_tourn.get('category')
        if category and isinstance(category, dict):
            cat_name = category.get('name')
            if cat_name != "WTA":
                return False
        else:
            return False  # category 缺失或格式不对
    else:
        return False  # uniqueTournament 缺失
    
    # 3. 过滤取消的比赛：检查 status.code 是否等于 70
    status = match.get('status')
    if status and isinstance(status, dict):
        status_code = status.get('code')
        if status_code == 70:
            return False  # 取消的比赛删除
    
    return True

for file_path in files:
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
        events = data.get('events', [])
        filtered = [m for m in events if keep_match(m)]
        all_events.extend(filtered)
        removed_count = len(events) - len(filtered)
        removed_pct = (removed_count/len(events)*100) if events else 0
    print(f"处理完成: {os.path.basename(file_path)} | 原始 {len(events)} 个 | 保留 {len(filtered)} 个 | 移除 {removed_count} 个 ({removed_pct:.1f}%)")

# 保存到原文件夹
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(all_events, f, indent=2, ensure_ascii=False)

print(f"\n合并完成！共保留 {len(all_events)} 个符合条件（WTA单打且未取消）的比赛")
print(f"文件已保存至: {output_file}")