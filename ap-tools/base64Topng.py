# 下面给出一个完整的 Python 脚本示例，脚本会：

# 1. 在当前目录下查找所有 “.jsonl” 文件；
# 2. 遍历每个文件中的每一行（假定每一行都是一个合法的 JSON 对象）；
# 3. 如果该对象存在 “screenshot_url” 字段，则认为其内容为 base64 编码的 PNG 图片数据；
# 4. 解码该 base64 图片数据后，随机生成一个文件名（存放在 “img” 目录下，如果该目录不存在会自动创建）并将图片保存为 PNG 格式；
# 5. 将 JSON 对象里 “screenshot_url” 字段的值替换为相对于当前目录的 “img/xxx.png” 路径；
# 6. 最后将处理后的 JSON 对象重新写回到原 jsonl 文件（本示例直接覆盖原文件，若需要保留原文件，可修改为另存为新文件）。

# 你可以根据实际情况进行调整。

# 脚本代码如下：

# ------------------------------------------------
#!/usr/bin/env python3
import os
import glob
import json
import base64
import uuid

def ensure_img_dir(directory="img"):
    if not os.path.exists(directory):
        os.makedirs(directory)
    return directory

def process_jsonl_file(filename, img_dir="img"):
    # 读取所有行
    with open(filename, "r", encoding="utf-8") as f:
        lines = f.readlines()

    new_lines = []
    for line in lines:
        line = line.strip()
        if not line:
            continue
        try:
            obj = json.loads(line)
        except Exception as e:
            print(f"解析 JSON 失败 {filename}: {e}")
            new_lines.append(line)
            continue

        # 判断是否存在 screenshot_url 字段
        if "screenshot_url" in obj and obj["screenshot_url"]:
            b64_data = obj["screenshot_url"]

            try:
                # 如果 base64 内容带有 "data:image/png;base64," 前缀，则去掉这部分
                if b64_data.startswith("data:image/png;base64,"):
                    b64_data = b64_data.split("data:image/png;base64,")[-1]
                # 解码 base64 数据
                image_bytes = base64.b64decode(b64_data)
            except Exception as e:
                print(f"base64 解码失败 {filename}: {e}")
                # 如果解码失败，跳过处理，保留原内容
            else:
                # 生成随机文件名
                random_filename = f"{uuid.uuid4().hex}.png"
                img_path = os.path.join(img_dir, random_filename)
                try:
                    with open(img_path, "wb") as img_file:
                        img_file.write(image_bytes)
                    # 使用相对路径更新 screenshot_url
                    obj["screenshot_url"] = img_path  # 此处 img_path 已经是相对路径
                except Exception as e:
                    print(f"保存图片失败 {img_path}: {e}")

        # 将更新后的 JSON 对象转换为一行字符串
        new_line = json.dumps(obj, ensure_ascii=False)
        new_lines.append(new_line)

    # 将处理后的所有行覆盖写回原文件
    with open(filename, "w", encoding="utf-8") as f:
        f.write("\n".join(new_lines))
        f.write("\n")  # 保证文件最后有换行

def main():
    # 确保图片存放目录存在
    img_dir = ensure_img_dir("img-7")
    # 查找当前目录下所有的 jsonl 文件
    jsonl_files = glob.glob("output-7/*.jsonl")
    if not jsonl_files:
        print("没有找到 jsonl 文件")
        return

    for file in jsonl_files:
        print(f"正在处理文件：{file}")
        process_jsonl_file(file, img_dir)
    print("处理完成")

if __name__ == "__main__":
    main()
# ------------------------------------------------

# 说明：

# 1. 脚本中使用 uuid.uuid4().hex 生成随机文件名，确保图片文件名不会重复。
# 2. 本脚本假定 jsonl 文件每行均为一个独立的 JSON 对象，如果有异常行则会原样保留。
# 3. 如果 base64 数据中带有 “data:image/png;base64,” 前缀，脚本会自动去掉该前缀再解码（可以根据实际情况调整）。
# 4. 处理过的 jsonl 文件会直接覆盖原文件，如需备份原文件，请提前做好备份。

# 保存该脚本为 convert_screenshots.py，然后在含有 .jsonl 文件的目录中运行：

#   python3 convert_screenshots.py

# 这样就能完成 base64 转 png 并更新 jsonl 内容的任务。