import asyncio
import os
import sys
from typing import List, Dict
from browser_use.llm.openai.chat import ChatOpenAI
from browser_use import Agent, BrowserConfig  # 引入浏览器配置
from dotenv import load_dotenv

# 加载环境变量（仅执行一次）
load_dotenv()
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # 修正文件路径写法

# 初始化全局模型（避免重复创建）
llm = ChatOpenAI(model='gpt-4.1-mini')

# 配置无头浏览器（全局共享）
browser_config = BrowserConfig(
    headless=True,  # 关键：启用无头模式
    timeout=60 * 1000,  # 超时时间（毫秒）
    slow_mo=200  # 可选：减缓操作速度（调试时可设为0）
)

# 模拟100个任务列表（实际可从文件/数据库读取）
task_list = [
    f"Find the founders of browser-use (Task {i})" 
    for i in range(1, 101)
]

async def process_task(task: str) -> Dict[str, str]:
    """处理单个任务的协程函数"""
    try:
        # 共享浏览器实例（每个任务使用独立页面）
        async with Agent(task=task, llm=llm, config=browser_config) as agent:
            result = await agent.run()
            return {"task": task, "result": result, "status": "success"}
    
    except Exception as e:
        return {"task": task, "error": str(e), "status": "failed"}

async def batch_execute(tasks: List[str]) -> List[Dict]:
    """批量执行任务并收集结果"""
    # 生成所有任务的协程对象
    tasks_coros = [process_task(task) for task in tasks]
    
    # 并发执行所有任务（利用asyncio.gather）
    return await asyncio.gather(*tasks_coros)

if __name__ == "__main__":
    import time
    start_time = time.time()
    
    # 执行批量任务
    results = asyncio.run(batch_execute(task_list))
    
    # 输出统计结果
    success_count = sum(1 for r in results if r["status"] == "success")
    print(f"\n任务执行完成：共{len(task_list)}个任务")
    print(f"成功：{success_count}个 | 失败：{len(task_list)-success_count}个")
    print(f"总耗时：{time.time()-start_time:.2f}秒")
    
    # 示例：保存结果到文件
    import json
    with open("batch_results.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)