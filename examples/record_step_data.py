# 根据文档信息，我现在为您提供一个完整的解决方案，将点击坐标信息集成到Browser Use的默认输出结构中。

# 完整的点击坐标记录解决方案
# 以下是一个完整的实现，它会将点击坐标信息添加到Browser Use的步骤输出中：

import asyncio
import json
import os
from pathlib import Path
from datetime import datetime
from browser_use import Agent
from browser_use.llm import ChatOpenAI

llm = ChatOpenAI(
	model='gpt-4o-mini',
)

class ClickCoordinateRecorder:
    """点击坐标记录器，集成到Browser Use的输出结构中"""
    
    def __init__(self, output_dir=None):
        # 使用Browser Use的默认输出目录或自定义目录
        if output_dir is None:
            self.output_dir = Path.home() / ".config" / "browseruse" / "events"
        else:
            self.output_dir = Path(output_dir)
        
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.step_counter = 0
        
    async def setup_click_tracking(self, agent):
        """设置页面级别的点击追踪"""
        page = await agent.browser_session.get_current_page()
        
        # 注入JavaScript代码来追踪所有点击事件
        await page.add_init_script("""
            window.browserUseClickTracker = {
                clicks: [],
                lastClickInfo: null,
                
                trackClick: function(event) {
                    const rect = event.target.getBoundingClientRect();
                    const clickInfo = {
                        timestamp: Date.now(),
                        coordinates: {
                            x: event.clientX,
                            y: event.clientY,
                            pageX: event.pageX,
                            pageY: event.pageY
                        },
                        elementBox: {
                            left: rect.left,
                            top: rect.top,
                            width: rect.width,
                            height: rect.height,
                            right: rect.right,
                            bottom: rect.bottom
                        },
                        target: {
                            tagName: event.target.tagName,
                            className: event.target.className,
                            id: event.target.id,
                            textContent: event.target.textContent?.substring(0, 100),
                            outerHTML: event.target.outerHTML?.substring(0, 200)
                        },
                        viewport: {
                            width: window.innerWidth,
                            height: window.innerHeight
                        }
                    };
                    
                    this.clicks.push(clickInfo);
                    this.lastClickInfo = clickInfo;
                    
                    // 标记最后点击的元素
                    document.querySelectorAll('[data-browser-use-last-clicked]').forEach(el => 
                        el.removeAttribute('data-browser-use-last-clicked')
                    );
                    event.target.setAttribute('data-browser-use-last-clicked', 'true');
                    
                    console.log('Browser Use: Click tracked', clickInfo);
                }
            };
            
            // 监听所有点击事件
            document.addEventListener('click', window.browserUseClickTracker.trackClick.bind(window.browserUseClickTracker), true);
            document.addEventListener('mousedown', window.browserUseClickTracker.trackClick.bind(window.browserUseClickTracker), true);
        """)

    async def record_step_with_coordinates(self, agent):
        """记录步骤信息，包含点击坐标"""
        self.step_counter += 1
        
        try:
            page = await agent.browser_session.get_current_page()
            
            # 获取基本的步骤信息
            step_data = await self._get_basic_step_data(agent)
            
            # 获取点击坐标信息
            click_data = await self._get_click_coordinates(page)
            
            # 检查最新的动作是否是点击动作
            latest_action = self._get_latest_action(agent)
            
            # 构建完整的步骤数据
            enhanced_step_data = {
                "session_id": self.session_id,
                "step_number": self.step_counter,
                "timestamp": datetime.now().isoformat(),
                "url": page.url,
                "title": await page.title(),
                
                # 基本步骤信息
                **step_data,
                
                # 点击坐标信息（如果有点击动作）
                "click_coordinates": click_data if self._is_click_action(latest_action) else None,
                
                # 最新动作信息
                "latest_action": latest_action,
                
                # 页面状态
                "page_state": {
                    "viewport": await page.evaluate("() => ({width: window.innerWidth, height: window.innerHeight})"),
                    "scroll_position": await page.evaluate("() => ({x: window.scrollX, y: window.scrollY})")
                }
            }
            
            # 保存到文件
            await self._save_step_data(enhanced_step_data)
            
            print(f"✅ 步骤 {self.step_counter} 已记录" + 
                  (f" (包含点击坐标: {click_data['coordinates'] if click_data else 'N/A'})" if click_data else ""))
            
        except Exception as e:
            print(f"❌ 记录步骤时出错: {e}")

    async def _get_basic_step_data(self, agent):
        """获取基本的步骤数据"""
        data = {}
        
        if hasattr(agent, "state") and agent.state.history:
            history = agent.state.history
            
            # 获取最新的各种信息
            model_thoughts = history.model_thoughts()
            if model_thoughts:
                data["model_thoughts"] = model_thoughts[-1] if model_thoughts else None
                
            model_outputs = history.model_outputs()
            if model_outputs:
                data["model_outputs"] = str(model_outputs[-1]) if model_outputs else None
                
            extracted_content = history.extracted_content()
            if extracted_content:
                data["extracted_content"] = extracted_content[-1] if extracted_content else None
                
            # 获取截图
            screenshots = history.screenshots()
            if screenshots:
                data["screenshot_path"] = screenshots[-1] if screenshots else None
        
        # 获取当前页面截图
        try:
            page = await agent.browser_session.get_current_page()
            screenshot_base64 = await agent.browser_session.take_screenshot()
            data["current_screenshot"] = screenshot_base64
        except:
            data["current_screenshot"] = None
            
        return data

    async def _get_click_coordinates(self, page):
        """获取点击坐标信息"""
        try:
            click_info = await page.evaluate("""
                () => {
                    if (window.browserUseClickTracker && window.browserUseClickTracker.lastClickInfo) {
                        return window.browserUseClickTracker.lastClickInfo;
                    }
                    return null;
                }
            """)
            return click_info
        except:
            return None

    def _get_latest_action(self, agent):
        """获取最新的动作信息"""
        try:
            if hasattr(agent, "state") and agent.state.history:
                model_actions = agent.state.history.model_actions()
                if model_actions:
                    latest = model_actions[-1]
                    return {
                        "action_name": getattr(latest, 'action', 'unknown'),
                        "parameters": getattr(latest, 'params', {}),
                        "timestamp": getattr(latest, 'timestamp', None)
                    }
        except:
            pass
        return None

    def _is_click_action(self, action):
        """判断是否是点击动作"""
        if not action:
            return False
        
        action_name = action.get('action_name', '').lower()
        click_keywords = ['click', 'tap', 'press', 'select']
        
        return any(keyword in action_name for keyword in click_keywords)

    async def _save_step_data(self, step_data):
        """保存步骤数据到文件"""
        # 创建文件名
        filename = f"session_{self.session_id}_step_{self.step_counter:03d}.json"
        filepath = self.output_dir / filename
        
        # 保存JSON文件
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(step_data, f, indent=2, ensure_ascii=False, default=str)
        
        # 同时保存一个汇总文件
        summary_file = self.output_dir / f"session_{self.session_id}_summary.json"
        
        # 读取现有汇总或创建新的
        if summary_file.exists():
            with open(summary_file, 'r', encoding='utf-8') as f:
                summary = json.load(f)
        else:
            summary = {
                "session_id": self.session_id,
                "start_time": datetime.now().isoformat(),
                "steps": []
            }
        
        # 添加当前步骤的摘要
        step_summary = {
            "step_number": self.step_counter,
            "timestamp": step_data["timestamp"],
            "url": step_data["url"],
            "action": step_data.get("latest_action", {}).get("action_name"),
            "has_click_coordinates": step_data["click_coordinates"] is not None,
            "click_coordinates": step_data["click_coordinates"]["coordinates"] if step_data["click_coordinates"] else None,
            "file_path": str(filepath)
        }
        
        summary["steps"].append(step_summary)
        summary["last_updated"] = datetime.now().isoformat()
        summary["total_steps"] = len(summary["steps"])
        
        # 保存汇总文件
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, ensure_ascii=False, default=str)

# 使用示例
async def main():
    """主函数示例"""
    
    # 创建点击坐标记录器
    recorder = ClickCoordinateRecorder()
    
    # 创建agent
    agent = Agent(
        task="访问百度，搜索'Browser Use'，然后点击第一个搜索结果",
        llm=llm
    )
    
    # 设置点击追踪的钩子函数
    async def setup_and_record(agent_obj):
        # 首次设置点击追踪
        await recorder.setup_click_tracking(agent_obj)
        # 记录步骤
        await recorder.record_step_with_coordinates(agent_obj)
    
    try:
        print(f"🚀 开始运行agent，输出目录: {recorder.output_dir}")
        print(f"📝 会话ID: {recorder.session_id}")
        
        # 运行agent，在每个步骤结束时记录信息
        await agent.run(
            on_step_end=setup_and_record,
            max_steps=10
        )
        
        print(f"✅ Agent运行完成！")
        print(f"📁 查看输出文件: {recorder.output_dir}")
        print(f"📊 汇总文件: {recorder.output_dir}/session_{recorder.session_id}_summary.json")
        
    except Exception as e:
        print(f"❌ 运行出错: {e}")

if __name__ == "__main__":
    asyncio.run(main())

