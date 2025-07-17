# import asyncio
# import json
# import os
# from pathlib import Path
# from typing import Dict, Any, List
# from browser_use import Agent, Controller, ActionResult
# from browser_use.llm import ChatOpenAI
# from browser_use.browser.session import BrowserSession
# from playwright.async_api import Page

# # 初始化 LLM 模型
# llm = ChatOpenAI(
#     model='gpt-4o-mini',
# )

# # 更简单的实现方式
# def setup_simple_coordinate_enhancement():
#     """设置简单的坐标增强"""
    
#     # 方法1: 增强截图方法
#     original_take_screenshot = BrowserSession.take_screenshot
    
#     async def enhanced_take_screenshot(self, *args, **kwargs):
#         """增强截图方法，同时记录元素坐标"""
        
#         # 调用原始截图方法
#         screenshot = await original_take_screenshot(self, *args, **kwargs)
        
#         try:
#             page = await self.get_current_page()
            
#             # 获取所有可点击元素的坐标
#             coordinates = await page.evaluate("""
#                 () => {
#                     const elements = [];
#                     document.querySelectorAll('*').forEach((el, index) => {
#                         const rect = el.getBoundingClientRect();
#                         const isClickable = ['A', 'BUTTON', 'INPUT', 'SELECT', 'TEXTAREA'].includes(el.tagName) ||
#                                            el.onclick || el.getAttribute('role') === 'button' ||
#                                            getComputedStyle(el).cursor === 'pointer';
                        
#                         if (isClickable && rect.width > 0 && rect.height > 0) {
#                             elements.push({
#                                 index: elements.length,
#                                 box: {
#                                     left: Math.round(rect.left),
#                                     top: Math.round(rect.top), 
#                                     width: Math.round(rect.width),
#                                     height: Math.round(rect.height)
#                                 },
#                                 center: {
#                                     x: Math.round(rect.left + rect.width/2),
#                                     y: Math.round(rect.top + rect.height/2)
#                                 },
#                                 tag: el.tagName,
#                                 text: el.textContent?.substring(0, 50) || ''
#                             });
#                         }
#                     });
#                     return elements;
#                 }
#             """)
            
#             # 将坐标信息存储到session中
#             self._elements_coordinates = coordinates
            
#             # 将坐标信息注入到页面中，供后续事件使用
#             await page.evaluate(f"""
#                 window.browserUseElementsCoordinates = {json.dumps(coordinates)};
#                 console.log('Browser Use: 已记录', {len(coordinates)}, '个元素坐标');
#             """)
            
#         except Exception as e:
#             print(f"Error getting coordinates: {e}")
        
#         return screenshot
    
#     # 应用补丁
#     BrowserSession.take_screenshot = enhanced_take_screenshot
    
#     # 方法2: 增强Controller的点击动作
#     from browser_use.controller.service import Controller
    
#     # 创建一个增强的Controller类
#     class EnhancedController(Controller):
#         def __init__(self, *args, **kwargs):
#             super().__init__(*args, **kwargs)
            
#             # 重写点击动作
#             @self.action('Click element by index with coordinates')
#             async def click_element_by_index_enhanced(index: int, page: Page) -> ActionResult:
#                 """增强版点击动作，包含坐标信息"""
                
#                 try:
#                     # 获取点击前的坐标信息
#                     click_info = await page.evaluate(f"""
#                         (index) => {{
#                             const coords = window.browserUseElementsCoordinates || [];
#                             if (index < coords.length) {{
#                                 const element = coords[index];
#                                 return {{
#                                     found: true,
#                                     ...element,
#                                     timestamp: Date.now()
#                                 }};
#                             }}
#                             return {{found: false}};
#                         }}
#                     """, index)
                    
#                     # 执行实际的点击
#                     elements = await page.query_selector_all('*')
#                     clickable_elements = []
                    
#                     for element in elements:
#                         is_clickable = await page.evaluate('''(element) => {
#                             const tagName = element.tagName.toLowerCase();
#                             return ['a', 'button', 'input', 'select', 'textarea'].includes(tagName) ||
#                                    element.onclick !== null ||
#                                    element.getAttribute('role') === 'button' ||
#                                    window.getComputedStyle(element).cursor === 'pointer';
#                         }''', element)
                        
#                         if is_clickable:
#                             clickable_elements.append(element)
                    
#                     if index < len(clickable_elements):
#                         await clickable_elements[index].click()
                        
#                         # 构建包含坐标信息的结果
#                         result_text = f"Clicked element {index}"
#                         if click_info.get('found'):
#                             coords = click_info['center']
#                             result_text += f" at coordinates ({coords['x']}, {coords['y']})"
                        
#                         return ActionResult(
#                             extracted_content=result_text,
#                             include_in_memory=True
#                         )
#                     else:
#                         return ActionResult(extracted_content=f"Element with index {index} not found")
                        
#                 except Exception as e:
#                     return ActionResult(extracted_content=f"Error clicking element {index}: {str(e)}")
    
#     # 替换默认的Controller
#     import browser_use
#     browser_use.Controller = EnhancedController
    
#     print("✅ 简单坐标增强已启用")
# # 使用示例
# async def main():
#     """使用坐标增强的Browser Use"""
    
#     # 方式2: 或者使用简单的增强方式
#     setup_simple_coordinate_enhancement()
    
#     # 创建agent
#     agent = Agent(
#         task="访问bing，搜索'Browser Use'，然后点击返回的第一个搜索结果",
#         llm=llm
#     )
    
#     try:
#         print("🚀 开始运行增强版Browser Use...")
        
#         # 运行agent
#         history = await agent.run(max_steps=10)
        
#         print("✅ Agent运行完成！")
#         print("📊 检查事件文件以查看坐标信息...")
        
#         # 检查生成的事件文件
#         events_dir = Path.home() / ".config" / "browseruse" / "events"
#         if events_dir.exists():
#             events_files = list(events_dir.glob("*.jsonl"))
#             if events_files:
#                 latest_file = max(events_files, key=os.path.getmtime)
#                 print(f"📄 最新事件文件: {latest_file}")
                
#                 with open(latest_file, 'r', encoding='utf-8') as f:
#                     lines = f.readlines()
                
#                 for i, line in enumerate(lines):
#                     try:
#                         event = json.loads(line.strip())
#                         if (event.get('event_type') == 'CreateAgentStepEvent' and 
#                             'actions' in event):
                            
#                             for action in event['actions']:
#                                 if 'click' in action.get('action', '').lower():
#                                     params = action.get('params', {})
#                                     if 'click_coordinates' in params:
#                                         print(f"\n🎯 发现包含坐标的点击事件:")
#                                         print(f"   动作: {action.get('action')}")
#                                         coords = params['click_coordinates']['click_position']
#                                         print(f"   点击坐标: ({coords['x']}, {coords['y']})")
#                                         box = params['click_coordinates']['element_box']
#                                         print(f"   元素区域: {box}")
                                        
#                     except json.JSONDecodeError:
#                         continue
        
#     except Exception as e:
#         print(f"❌ 运行出错: {e}")

# if __name__ == "__main__":
#     # 运行增强版Browser Use
#     asyncio.run(main())
