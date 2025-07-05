import requests
import json
import os
import sys
import urllib.parse # 导入 urllib.parse 模块用于 URL 解析

# 定义要获取内容的 URL
# 请将此 URL 替换为你实际的目标 TXT 文件 URL
TARGET_URL = "https://cf.trackerslist.com/best.txt" # 替换为你的实际 URL
OUTPUT_FILE = "tracker.json"

def fetch_txt_content(url):
    """
    从指定 URL 获取 TXT 内容。
    """
    try:
        response = requests.get(url)
        response.raise_for_status() # 如果请求不成功（例如 4xx 或 5xx 错误），则抛出 HTTPError
        return response.text
    except requests.exceptions.RequestException as e:
        print(f"Error fetching content from {url}: {e}", file=sys.stderr)
        return None

def convert_txt_to_json(txt_content):
    """
    将 TXT 内容转换为 JSON 格式。
    此函数将处理每行一个 URL 的 TXT 内容，提取其中的域名，并将其转换为以下 JSON 格式：
    {
      "version": 3,
      "rules":[
        {
          "domain":[]
        }
      ]
    }
    TXT 中的每个提取出的域名都将作为字符串添加到 rules[0].domain 列表中。
    """
    # 初始化 JSON 结构
    json_data = {
      "version": 3,
      "rules": [
        {
          "domain": []
        }
      ]
    }

    if not txt_content:
        return json_data

    lines = txt_content.strip().split('\n')
    for line in lines:
        url_string = line.strip()
        if not url_string: # 跳过空行
            continue

        try:
            # 解析 URL
            parsed_url = urllib.parse.urlparse(url_string)
            # netloc 包含主机名和端口（如果存在）
            netloc = parsed_url.netloc

            # 从 netloc 中提取域名，去除端口（如果存在）
            # 例如 "example.com:80" 会变成 "example.com"
            domain_only = netloc.split(':')[0]

            if domain_only: # 确保提取到的域名不为空
                json_data["rules"][0]["domain"].append(domain_only)
            else:
                print(f"Warning: Could not extract domain from URL: {url_string}", file=sys.stderr)

        except Exception as e:
            print(f"Error parsing URL '{url_string}': {e}", file=sys.stderr)
            # 可以选择在这里跳过此行或进行其他错误处理

    return json_data

def save_json_to_file(json_data, file_path):
    """
    将 JSON 数据保存到指定文件。
    """
    try:
        # 确保输出目录存在
        output_dir = os.path.dirname(file_path)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)

        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(json_data, f, ensure_ascii=False, indent=4)
        print(f"Successfully saved JSON to {file_path}")
        return True
    except IOError as e:
        print(f"Error saving JSON to {file_path}: {e}", file=sys.stderr)
        return False

def main():
    """
    主函数：获取、转换并保存数据。
    """
    print(f"Attempting to fetch data from: {TARGET_URL}")
    txt_content = fetch_txt_content(TARGET_URL)

    if txt_content is None:
        print("Failed to fetch TXT content. Exiting.", file=sys.stderr)
        sys.exit(1) # 退出并指示失败

    print("TXT content fetched successfully. Converting to JSON...")
    json_data = convert_txt_to_json(txt_content)

    if not json_data:
        print("No data converted to JSON. Check TXT format or URL content.", file=sys.stderr)
        # 即使没有数据转换，也尝试保存一个空 JSON 对象，或者根据需求决定是否退出
        # sys.exit(1)

    print("JSON conversion complete. Saving to file...")
    if not save_json_to_file(json_data, OUTPUT_FILE):
        print("Failed to save JSON data. Exiting.", file=sys.stderr)
        sys.exit(1) # 退出并指示失败

if __name__ == "__main__":
    main()
