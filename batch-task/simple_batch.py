# 下面给出修改后的示例代码，任务文本不再是固定的 TASK_TEXT，而是从一个 JSONL 文件中读取，每行格式类似于：

#   {"taskText": "Find the founders of browser-use"}

# 代码会逐行读取文件，并将每个任务的 taskText 提取出来，添加到任务列表中，然后按设定的并发量执行，并记录每个任务的执行结果到以唯一 id 命名的 JSON 文件中。

# ──────────────────────────────
#!/usr/bin/env python3
import asyncio
import os
import sys
import time
import json
import random

from typing import List

# 导入环境变量
from dotenv import load_dotenv
load_dotenv()

# 添加工程根目录到python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 导入现有的包、类
from browser_use.controller.service import Controller
from browser_use.llm.openai.chat import ChatOpenAI
from browser_use.browser.profile import BrowserProfile
from browser_use.browser.session import BrowserSession
from browser_use import Agent, BrowserConfig

from pydantic import BaseModel

# 定义结果输出格式（此处仅作为示例）
class Post(BaseModel):
    post_title: str
    post_url: str
    num_comments: int
    hours_since_post: int

class Posts(BaseModel):
    posts: List[Post]

# 初始化 Controller，用来进行数据处理（如果需要）
controller = Controller(output_model=Posts)

# 配置无头浏览器（全局共享）
browser_config = BrowserConfig(
    headless=True,      # 启用无头模式
    timeout=60 * 1000,  # 超时时间，单位为毫秒
    slow_mo=200         # 渐进式操作间隔，调试时可适当调低速度
)


MAX_STEPS = 10

CONCURRENT_TASKS = 2


# 初始化 LLM 模型
llm = ChatOpenAI(
    model='gpt-4o-mini',
)

# 创建共享的 browser_session
browser_session = BrowserSession(
    browser_profile=BrowserProfile(
        keep_alive=True,
        user_data_dir=None,
        headless=True,
    )
)

# 定义从 JSONL 文件中加载任务的方法
def load_tasks_from_jsonl(file_path: str) -> List[str]:
    tasks = []
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    json_obj = json.loads(line)
                    # 读取 JSON 对象中的 taskText 字段（注意字段名称区分大小写）
                    task_text = json_obj.get("taskText")
                    if task_text:
                        tasks.append(task_text)
                    else:
                        print(f"Warning: 未找到 taskText 字段： {line}")
                except Exception as e_parse:
                    print(f"Error parsing line: {line} \nError: {e_parse}")
    except Exception as e_file:
        print(f"Error opening file {file_path}: {e_file}")
    return tasks

# 定义单个任务的执行逻辑
async def run_single_task(task_text: str, semaphore: asyncio.Semaphore) -> dict:
    async with semaphore:
        # 生成唯一 ID（时间戳 + 随机数字）
        task_id = f"{int(time.time() * 1000)}_{random.randint(1000, 9999)}" 
        # 每个任务创建一个新的 Agent 实例
        agent = Agent(task=task_text, llm=llm, browser_session=browser_session, config=browser_config)
        try:
            result = await agent.run(max_steps=MAX_STEPS)
            status = "successful" if result.is_successful else "not successful"
            # 如果 result 是 pydantic 对象，可通过 dict() 方法转换，否则尝试转换为 str
            result_data = result.dict() if hasattr(result, "dict") else str(result)
            output = {
                "id": task_id,
                "task": task_text,
                "success": result.is_successful,
                "status": status,
                "result": result_data,
            }
        except Exception as e:
            output = {
                "id": task_id,
                "task": task_text,
                "success": False,
                "error": str(e)
            }
        # 将结果保存到文件，文件名以任务 ID 命名
        result_filename = f"{task_id}.json"
        try:
          with open(config_path, 'w') as f:
				json.dump(new_config.model_dump(), f, indent=2)
            with open(result_filename, "w", encoding="utf-8") as f:
                json.dump(output, f, ensure_ascii=False, indent=4)
            print(f"Task {task_id} completed. Result saved to {result_filename}")
        except Exception as e_file:
            print(f"Task {task_id} completed, but failed to write file: {e_file}")
        return output

# main 函数：先启动共享 browser_session，再加载任务并并发调度全部任务
async def main():
    # 启动共享 browser_session
    await browser_session.start()

    # 从指定的 JSONL 文件中加载所有任务文本（确保文件路径正确）
    tasks_file = "tasks.jsonl"  # 根据实际情况修改 JSONL 文件路径
    task_texts = load_tasks_from_jsonl(tasks_file)
    if not task_texts:
        print("未加载到任何任务，程序退出。")
        return

    # 定义并发量，例如设置为同时运行 5 个任务
    concurrent_tasks = CONCURRENT_TASKS
    semaphore = asyncio.Semaphore(concurrent_tasks)

    # 构造 asyncio 任务列表，每个任务执行单个任务逻辑
    tasks = [run_single_task(task_text, semaphore) for task_text in task_texts]

    # 并发运行所有任务，等待所有任务结束
    results = await asyncio.gather(*tasks)
    print("All tasks finished.")

    # 结束 browser_session（若有对应方法）
    if hasattr(browser_session, "close"):
        await browser_session.close()

if __name__ == '__main__':
    asyncio.run(main())
# ──────────────────────────────

# 代码说明：

# 1. load_tasks_from_jsonl(file_path) 函数负责打开并按行读取 JSONL 文件，每行解析为 JSON 后提取 taskText 字段，将其存入任务列表。
# 2. run_single_task() 函数与之前类似，在进入信号量保护区域后生成唯一 id，进行单个任务的执行，并将结果保存为 JSON 文件。
# 3. main() 函数首先启动 browser_session，然后调用 load_tasks_from_jsonl() 加载任务列表，如果有任务，则根据设定的并发量（通过 Semaphore 控制）构造并发任务并等待全部结束，最后关闭 browser_session。
# 4. 请根据实际情况调整 tasks_file 的文件路径及其他配置参数。

# 这样修改后，每行 JSONL 中的任务文本都会被读取出来，并发运行，每个任务的执行结果都会记录到以唯一 ID 命名的 JSON 文件中。