import os
import glob
import datetime
import re
from datetime import timezone, timedelta

# 设置上海时区 (UTC+8)
shanghai_tz = timezone(timedelta(hours=8))
now = datetime.datetime.now(shanghai_tz)
print(f"Conversion started at: {now.strftime('%Y-%m-%d %H:%M:%S')} Asia/Shanghai")

# 确保输出目录存在
os.makedirs("output/rtp", exist_ok=True)

# 频道LOGO基础URL
LOGO_BASE_URL = "https://gitee.com/ysx88/TVlogo/raw/main/img/"

# 频道分组和标识映射
def get_channel_info(channel_name):
    # 频道名称标准化和清理
    clean_name = channel_name.strip()
    
    # 初始化返回数据
    info = {
        "tvg_id": clean_name,
        "tvg_name": clean_name,
        "tvg_logo": "",
        "group_title": "📺其他频道",
        "sort_key": clean_name  # 初始排序键
    }
    
    # CCTV频道处理
    if re.search(r'^CCTV', clean_name, re.IGNORECASE):
        # 提取CCTV后面的数字或名称
        cctv_match = re.search(r'^CCTV[-\s]*(\d+)[\s]*(.*?)$', clean_name, re.IGNORECASE)
        if cctv_match:
            cctv_num = cctv_match.group(1)
            # 生成标准化的频道名称
            std_name = f"CCTV-{cctv_num}"
            info["tvg_id"] = std_name
            info["tvg_name"] = std_name
            info["tvg_logo"] = f"{LOGO_BASE_URL}CCTV{cctv_num}.png"
            info["group_title"] = "📺央视频道"
            # 为CCTV设置排序键，确保数字顺序
            info["sort_key"] = f"CCTV{int(cctv_num):02d}"
        else:
            # 处理如CCTV-新闻等特殊频道
            info["tvg_logo"] = f"{LOGO_BASE_URL}CCTV.png"
            info["group_title"] = "📺央视频道"
            # 将非数字CCTV放在最后
            info["sort_key"] = f"CCTV99{clean_name}"
    
    # 卫视频道处理
    elif re.search(r'卫视$', clean_name):
        # 提取卫视名称
        ws_match = re.search(r'^(.+)卫视$', clean_name)
        if ws_match:
            ws_name = ws_match.group(1)
            info["tvg_logo"] = f"{LOGO_BASE_URL}{ws_name}卫视.png"
            info["group_title"] = "📺卫视频道"
            # 按省份名称排序
            info["sort_key"] = f"卫视{ws_name}"
    
    # 简化分组 - 只分为四个大类
    elif re.search(r'(上海|北京|广东|浙江|江苏|湖南|湖北|山东|山西|辽宁|吉林|黑龙江|四川|重庆|贵州|云南|河南|河北|安徽|福建|江西|陕西|甘肃|宁夏|新疆|青海|内蒙古|西藏|香港|澳门|台湾)', clean_name):
        info["group_title"] = "📺地方频道"
        # 尝试匹配地方台logo
        region_match = re.search(r'^([\u4e00-\u9fff]+)(卫视|电视台|综合|新闻|都市|生活|影视|娱乐)', clean_name)
        if region_match:
            region = region_match.group(1)
            info["tvg_logo"] = f"{LOGO_BASE_URL}{region}.png"
    
    # 所有专题频道归为一类
    elif re.search(r'(CHC|电影|影视|剧场|体育|足球|NBA|音乐|MTV|新闻|资讯|少儿|动画|卡通|纪录片|探索|Discovery|国家地理)', clean_name):
        info["group_title"] = "📺专题频道"
        
        # 尝试为特定类型频道生成logo
        if "CHC" in clean_name:
            info["tvg_logo"] = f"{LOGO_BASE_URL}CHC.png"
        elif "体育" in clean_name:
            info["tvg_logo"] = f"{LOGO_BASE_URL}体育.png"
        elif "音乐" in clean_name:
            info["tvg_logo"] = f"{LOGO_BASE_URL}音乐.png"
        elif "少儿" in clean_name or "动画" in clean_name:
            info["tvg_logo"] = f"{LOGO_BASE_URL}少儿.png"
        elif "纪录" in clean_name or "探索" in clean_name:
            info["tvg_logo"] = f"{LOGO_BASE_URL}纪录.png"
        elif "电影" in clean_name or "影视" in clean_name:
            info["tvg_logo"] = f"{LOGO_BASE_URL}电影.png"
        
    # 尝试为没有匹配到特定规则的频道生成logo URL
    if not info["tvg_logo"] and not re.search(r'(测试|备用|购物)', clean_name):
        # 移除常见后缀和特殊字符，尝试生成通用logo URL
        base_name = re.sub(r'[超高清]+$|[0-9]+$|[-\s]+$', '', clean_name)
        base_name = re.sub(r'[^\w\u4e00-\u9fff]+', '', base_name)
        if base_name:
            info["tvg_logo"] = f"{LOGO_BASE_URL}{base_name}.png"
    
    return info

# 直接获取config/rtp目录下的所有txt文件
rtp_files = glob.glob("config/rtp/*.txt")

if not rtp_files:
    print("WARNING: No RTP files found in config/rtp directory!")
    # 检查目录是否存在
    if not os.path.exists("config/rtp"):
        print("The config/rtp directory does not exist!")
    else:
        print("Directory exists but no .txt files found.")
        print("Files in config/rtp directory:")
        for file in os.listdir("config/rtp"):
            print(f"  - {os.path.join('config/rtp', file)}")
else:
    print(f"Found {len(rtp_files)} RTP files to process:")
    for file in rtp_files:
        print(f"  - {file}")

for rtp_file in rtp_files:
    # 获取文件名（不含扩展名）作为地区名
    file_name = os.path.basename(rtp_file)
    area_name = os.path.splitext(file_name)[0]  # 去掉.txt扩展名
        
    # 创建对应的输出文件
    output_file = f"output/rtp/{area_name}.m3u"
    
    print(f"Processing {rtp_file} -> {output_file}")
    
    try:
        # 读取RTP文件
        with open(rtp_file, "r", encoding="utf-8") as f:
            lines = f.readlines()
        
        # 创建分组字典存储各组频道
        grouped_channels = {}
        
        # 首先按组分类所有频道
        for line in lines:
            line = line.strip()
            # 跳过空行和注释行
            if not line or line.startswith("#"):
                continue
                
            # 解析RTP地址行，格式可能是: 频道名,rtp://IP:端口
            parts = line.split(",")
            if len(parts) >= 2:
                channel_name = parts[0].strip()
                rtp_address = parts[1].strip()
                
                # 获取频道信息
                channel_info = get_channel_info(channel_name)
                
                # 将频道添加到相应的组
                group = channel_info["group_title"]
                if group not in grouped_channels:
                    grouped_channels[group] = []
                
                grouped_channels[group].append((channel_name, rtp_address, channel_info))
        
        # 创建M3U文件
        with open(output_file, "w", encoding="utf-8") as f:
            # 写入M3U头部
            f.write("#EXTM3U\n")
            # 添加转换时间注释（上海时间）
            f.write(f"#Created by GitHub Actions: {now.strftime('%Y-%m-%d %H:%M:%S')} Asia/Shanghai\n")
            f.write(f"#Source: {area_name}\n\n")
            
            # 统计处理的频道数
            total_channel_count = 0
            
            # 定义组的显示顺序 - 使用简化的四个分组
            group_order = [
                "📺央视频道", 
                "📺卫视频道", 
                "📺地方频道", 
                "📺专题频道", 
                "📺其他频道"
            ]
            
            # 按组顺序写入频道
            for group in group_order:
                if group in grouped_channels and grouped_channels[group]:
                    # 按自定义排序键排序，确保CCTV按数字顺序等
                    channels = sorted(grouped_channels[group], key=lambda x: x[2]["sort_key"])
                    
                    # 写入组内所有频道
                    for channel_name, rtp_address, info in channels:
                        tvg_id = info["tvg_id"]
                        tvg_name = info["tvg_name"]
                        tvg_logo = info["tvg_logo"]
                        group_title = info["group_title"]
                        
                        # 生成完整的EXTINF行
                        f.write(f'#EXTINF:-1 tvg-name="{tvg_name}" tvg-logo="{tvg_logo}" group-title="{group_title}",{channel_name}\n')
                        f.write(f"{rtp_address}\n")
                        total_channel_count += 1
        
        print(f"Created M3U file: {output_file} with {total_channel_count} channels in {len(grouped_channels)} groups")
    except Exception as e:
        print(f"Error processing {rtp_file}: {str(e)}")

print("Conversion completed!")
