# get_current_page(): 获取当前页面
# take_screenshot(): 截图
# get_page_html(): 获取页面HTML
# 让我提供一个正确的解决方案，通过修改Browser Use的核心组件来添加坐标信息：

import asyncio
from hmac import new
import json
import os
from pathlib import Path
import time
from typing import Dict, Any, List
from browser_use import Agent, Controller, ActionResult
# from browser_use.browser_use_agent import BrowserUseAgent
from browser_use.llm import ChatOpenAI
from browser_use.llm import ChatAzureOpenAI
from browser_use.browser.session import BrowserSession
from playwright.async_api import Page
from browser_use.llm import ChatDeepSeek
from utils.llm_provider import get_llm_model

# llm = get_llm_model(
#     provider="openai",
#     model_name="gpt-4o-mini",
#     temperature=0.8,
# )

# # 初始化 LLM 模型

# openai
# llm = ChatOpenAI(
#     model='gpt-4o-mini',
# )


# # Retrieve Azure-specific environment variables
azure_openai_api_key = os.getenv('AZURE_OPENAI_KEY')
azure_openai_endpoint = os.getenv('AZURE_OPENAI_ENDPOINT')
llm = ChatAzureOpenAI(
    model='gpt-4o-mini',
    api_key=azure_openai_api_key,
    # Corrected to use azure_endpoint instead of openai_api_base
    azure_endpoint=azure_openai_endpoint,
)

# deepseek
# deepseek_endpoint = os.getenv('DEEPSEEK_ENDPOINT')
# deepseek_api_key = os.getenv('DEEPSEEK_API_KEY')
# llm = ChatDeepSeek(
#     base_url='https://ark.cn-beijing.volces.com/api/v3',
#     model='deepseek-v3-250324',
#     api_key=deepseek_api_key,
# )

# 全局存储原始方法
_original_methods = {}


# class BrowserUseCoordinateEnhancer:
#     """通过monkey patching增强Browser Use，在默认输出中添加坐标信息"""

#     def __init__(self):
#         _original_methods = {}
#         self.applied_patches = False
#         self.click_coordinates_cache = {}

#     def apply_patches(self):
#         """应用所有补丁"""
#         if self.applied_patches:
#             return

#         self._patch_browser_session_screenshot()
#         self._patch_controller_actions()
#         self.applied_patches = True
#         print("✅ Browser Use坐标增强补丁已应用")

#     def _patch_browser_session_screenshot(self):
#         """补丁BrowserSession的截图方法，同时记录元素坐标"""

#         # 保存原始方法
#         _original_methods['take_screenshot'] = BrowserSession.take_screenshot

#         async def enhanced_take_screenshot(self, *args, **kwargs):
#             """增强的截图方法，同时获取所有可点击元素的坐标"""

#             # 调用原始截图方法
#             screenshot = await _original_methods['take_screenshot'](self, *args, **kwargs)

#             try:
#                 page = await self.get_current_page()

#                 # 获取所有可点击元素的坐标信息
#                 elements_coordinates = await page.evaluate("""
#                     () => {
#                         const elements = [];
#                         const allElements = document.querySelectorAll('*');
                        
#                         for (let i = 0; i < allElements.length; i++) {
#                             const element = allElements[i];
                            
#                             // 检查元素是否可点击
#                             const tagName = element.tagName.toLowerCase();
#                             const isClickable = ['a', 'button', 'input', 'select', 'textarea', 'label'].includes(tagName) ||
#                                               element.onclick !== null ||
#                                               element.getAttribute('role') === 'button' ||
#                                               element.getAttribute('role') === 'link' ||
#                                               element.getAttribute('tabindex') !== null ||
#                                               window.getComputedStyle(element).cursor === 'pointer';
                            
#                             if (isClickable && element.offsetParent !== null) {
#                                 const rect = element.getBoundingClientRect();
                                
#                                 // 只包含在视口内且有实际大小的元素
#                                 if (rect.width > 0 && rect.height > 0 && 
#                                     rect.top >= 0 && rect.left >= 0 && 
#                                     rect.bottom <= window.innerHeight && 
#                                     rect.right <= window.innerWidth) {
                                    
#                                     elements.push({
#                                         index: elements.length,
#                                         tagName: tagName,
#                                         text: element.textContent?.trim().substring(0, 100) || '',
#                                         className: element.className || '',
#                                         id: element.id || '',
#                                         href: element.href || null,
#                                         type: element.type || null,
#                                         placeholder: element.placeholder || null,
#                                         value: element.value || null,
#                                         box: {
#                                             left: Math.round(rect.left),
#                                             top: Math.round(rect.top),
#                                             width: Math.round(rect.width),
#                                             height: Math.round(rect.height),
#                                             right: Math.round(rect.right),
#                                             bottom: Math.round(rect.bottom)
#                                         },
#                                         center: {
#                                             x: Math.round(rect.left + rect.width / 2),
#                                             y: Math.round(rect.top + rect.height / 2)
#                                         },
#                                         viewport: {
#                                             width: window.innerWidth,
#                                             height: window.innerHeight,
#                                             scrollX: window.scrollX,
#                                             scrollY: window.scrollY
#                                         }
#                                     });
#                                 }
#                             }
#                         }
                        
#                         return elements;
#                     }
#                 """)

#                 # 将坐标信息存储到session中，供后续使用
#                 self._last_elements_coordinates = elements_coordinates
#                 self._last_screenshot_timestamp = await page.evaluate('Date.now()')

#                 print(f"📍 已记录 {len(elements_coordinates)} 个可点击元素的坐标")

#             except Exception as e:
#                 print(f"❌ 获取元素坐标时出错: {e}")

#             return screenshot

#         # 应用补丁
#         BrowserSession.take_screenshot = enhanced_take_screenshot

#     def _patch_controller_actions(self):
#         """补丁Controller的动作，添加坐标记录"""

#         # 获取Controller类
#         from browser_use.controller.service import Controller

#         controller = Controller()

#         # 保存原始的registry执行方法
#         if hasattr(controller, 'registry'):
#             original_execute = getattr(
#                 controller.registry, 'execute_action', None)
#             if original_execute:
#                 _original_methods['execute_action'] = original_execute

#                 async def enhanced_execute_action(action_name: str, params: dict, **kwargs):
#                     """增强的动作执行，记录点击坐标"""

#                     # 如果是点击动作，先记录坐标信息
#                     if 'click' in action_name.lower():
#                         await self._record_click_coordinates(action_name, params, kwargs)

#                     # 调用原始方法
#                     result = await _original_methods['execute_action'](action_name, params, **kwargs)

#                     return result

#                 # 应用补丁
#                 controller.registry.execute_action = enhanced_execute_action

#     async def _record_click_coordinates(self, action_name: str, params: dict, kwargs: dict):
#         """记录点击坐标信息"""
#         try:
#             # 获取browser_session
#             browser_session = kwargs.get('browser_session')
#             if not browser_session:
#                 return

#             page = await browser_session.get_current_page()
#             index = params.get('index')

#             if index is not None:
#                 # 获取点击元素的坐标信息
#                 click_info = await page.evaluate(f"""
#                     (index) => {{
#                         const elements = [];
#                         const allElements = document.querySelectorAll('*');
                        
#                         for (let i = 0; i < allElements.length; i++) {{
#                             const element = allElements[i];
#                             const tagName = element.tagName.toLowerCase();
#                             const isClickable = ['a', 'button', 'input', 'select', 'textarea', 'label'].includes(tagName) ||
#                                               element.onclick !== null ||
#                                               element.getAttribute('role') === 'button' ||
#                                               element.getAttribute('role') === 'link' ||
#                                               element.getAttribute('tabindex') !== null ||
#                                               window.getComputedStyle(element).cursor === 'pointer';
                            
#                             if (isClickable && element.offsetParent !== null) {{
#                                 elements.push(element);
#                             }}
#                         }}
                        
#                         if (index < elements.length) {{
#                             const element = elements[index];
#                             const rect = element.getBoundingClientRect();
                            
#                             return {{
#                                 found: true,
#                                 tagName: element.tagName,
#                                 text: element.textContent?.trim().substring(0, 100) || '',
#                                 className: element.className || '',
#                                 id: element.id || '',
#                                 box: {{
#                                     left: Math.round(rect.left),
#                                     top: Math.round(rect.top),
#                                     width: Math.round(rect.width),
#                                     height: Math.round(rect.height),
#                                     right: Math.round(rect.right),
#                                     bottom: Math.round(rect.bottom)
#                                 }},
#                                 click_coordinates: {{
#                                     x: Math.round(rect.left + rect.width / 2),
#                                     y: Math.round(rect.top + rect.height / 2),
#                                     pageX: Math.round(rect.left + rect.width / 2 + window.scrollX),
#                                     pageY: Math.round(rect.top + rect.height / 2 + window.scrollY)
#                                 }},
#                                 viewport: {{
#                                     width: window.innerWidth,
#                                     height: window.innerHeight,
#                                     scrollX: window.scrollX,
#                                     scrollY: window.scrollY
#                                 }},
#                                 timestamp: Date.now()
#                             }};
#                         }}
                        
#                         return {{found: false}};
#                     }}
#                 """, index)

#                 if click_info.get('found'):
#                     # 缓存点击信息
#                     self.click_coordinates_cache[f"{action_name}_{index}"] = click_info

#                     # 将坐标信息添加到params中，这样会被包含在事件输出中
#                     params['click_coordinates'] = {
#                         'click_position': click_info['click_coordinates'],
#                         'element_box': click_info['box'],
#                         'element_info': {
#                             'tagName': click_info['tagName'],
#                             'text': click_info['text'],
#                             'className': click_info['className'],
#                             'id': click_info['id']
#                         },
#                         'viewport': click_info['viewport'],
#                         'timestamp': click_info['timestamp']
#                     }

#                     print(
#                         f"🎯 已记录点击坐标: ({click_info['click_coordinates']['x']}, {click_info['click_coordinates']['y']})")

#         except Exception as e:
#             print(f"❌ 记录点击坐标时出错: {e}")


# 使用示例
async def main():
    """使用坐标增强的Browser Use"""

    # 方式1: 使用完整的增强器
    # enhancer = BrowserUseCoordinateEnhancer()
    # enhancer.apply_patches()

    # 方式2: 或者使用简单的增强方式
    # setup_simple_coordinate_enhancement()

    # 每个任务创建一个新的 Agent 实例
    agent = Agent(task='在浏览器中访问trip.com，查询7月16日上海到成都最便宜的机票', llm=llm,
                  appen_task_id=str(int(time.time())),
                  browser_session=browser_session, config=browser_config)

    try:
        print("🚀 开始运行增强版Browser Use...")

        # 运行agent
        history = await agent.run(max_steps=10)

        print("✅ Agent运行完成！")
        print("📊 检查事件文件以查看坐标信息...")

        # 检查生成的事件文件
        events_dir = Path.home() / ".config" / "browseruse" / "events"
        if events_dir.exists():
            events_files = list(events_dir.glob("*.jsonl"))
            if events_files:
                latest_file = max(events_files, key=os.path.getmtime)
                print(f"📄 最新事件文件: {latest_file}")

                with open(latest_file, 'r', encoding='utf-8') as f:
                    lines = f.readlines()

                for i, line in enumerate(lines):
                    try:
                        event = json.loads(line.strip())
                        if (event.get('event_type') == 'CreateAgentStepEvent' and
                                'actions' in event):

                            for action in event['actions']:
                                if 'click' in action.get('action', '').lower():
                                    params = action.get('params', {})
                                    if 'click_coordinates' in params:
                                        print(f"\n🎯 发现包含坐标的点击事件:")
                                        print(f"   动作: {action.get('action')}")
                                        coords = params['click_coordinates']['click_position']
                                        print(
                                            f"   点击坐标: ({coords['x']}, {coords['y']})")
                                        box = params['click_coordinates']['element_box']
                                        print(f"   元素区域: {box}")

                    except json.JSONDecodeError:
                        continue

    except Exception as e:
        print(f"❌ 运行出错: {e}")

if __name__ == "__main__":
    # 运行增强版Browser Use
    asyncio.run(main())

# 关键改进
# 正确的方法补丁：

# 补丁BrowserSession.take_screenshot()而不是不存在的get_page_state()
# 补丁Controller的动作执行方法
# 坐标信息集成：

# 在截图时记录所有可点击元素的坐标
# 在点击动作执行时，将坐标信息直接添加到params中
# 这样坐标信息会自动包含在生成的事件JSON中
# 简单使用：

# # 只需要在导入后调用一次
# setup_simple_coordinate_enhancement()

# # 然后正常使用Browser Use
# agent = Agent(task="你的任务", llm=ChatOpenAI(model="gpt-4o"))
# await agent.run()

# 输出格式： 生成的JSONL事件文件中，点击动作会包含：
# {
#   "event_type": "CreateAgentStepEvent",
#   "actions": [
#     {
#       "action": "click_element_by_index",
#       "params": {
#         "index": 5,
#         "click_coordinates": {
#           "click_position": {"x": 500, "y": 300},
#           "element_box": {"left": 450, "top": 280, "width": 100, "height": 40},
#           "element_info": {"tagName": "BUTTON", "text": "搜索"},
#           "viewport": {"width": 1920, "height": 1080},
#           "timestamp": 1705394622123
#         }
#       }
#     }
#   ]
# }

# 这个解决方案通过monkey patching修改了Browser Use的核心方法，使其在生成事件时就包含坐标信息，无需修改源码。

# Ask a question...
