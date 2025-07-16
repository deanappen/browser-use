import json
import os

def split_jsonl_to_files(input_file, output_dir, filename_prefix="record", filename_field=None):
    """
    将 JSONL 文件中的每行 JSON 写入单独的 JSON 文件。
    
    Args:
        input_file (str): 输入的 JSONL 文件路径
        output_dir (str): 输出目录路径
        filename_prefix (str): 输出文件名前缀（默认为 "record"）
        filename_field (str, optional): 用于命名的 JSON 字段（如果提供）
    """
    # 确保输出目录存在
    os.makedirs(output_dir, exist_ok=True)
    
    # 打开 JSONL 文件
    with open(input_file, 'r', encoding='utf-8') as f:
        for index, line in enumerate(f):
            try:
                # 解析每行的 JSON 数据
                json_data = json.loads(line.strip())
                
                # 确定输出文件名
                if filename_field and filename_field in json_data:
                    # 使用 JSON 中的指定字段作为文件名的一部分
                    filename = f"{filename_prefix}_{json_data[filename_field]}.json"
                else:
                    # 使用索引作为文件名的一部分
                    filename = f"{filename_prefix}_{index}.json"
                
                # 构造输出文件路径
                output_path = os.path.join(output_dir, filename)
                
                # 将 JSON 数据写入单独文件
                with open(output_path, 'w', encoding='utf-8') as out_file:
                    json.dump(json_data, out_file, ensure_ascii=False, indent=2)
                    
                print(f"Written: {output_path}")
                
            except json.JSONDecodeError as e:
                print(f"Error parsing line {index + 1}: {e}")
            except Exception as e:
                print(f"Error processing line {index + 1}: {e}")

if __name__ == "__main__":
    # 示例用法
    input_file = "/Users/vincent/.config/browseruse/events/068777c3-a3ab-7335-8000-70f6ae6050b2.jsonl"  # 输入 JSONL 文件
    output_dir = "output_json_files"  # 输出目录
    filename_prefix = "record"  # 文件名前缀
    filename_field = None  # 可选：使用 JSON 中的某个字段作为文件名
    
    split_jsonl_to_files(input_file, output_dir, filename_prefix, filename_field)