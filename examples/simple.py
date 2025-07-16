import asyncio
import os
import sys
from typing import List

from browser_use.controller.service import Controller
from browser_use.llm.openai.chat import ChatOpenAI
from browser_use.browser.profile import BrowserProfile
from browser_use.browser.session import BrowserSession

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv

load_dotenv()


from browser_use import Agent, BrowserConfig

from pydantic import BaseModel
# Define the output format as a Pydantic model
class Post(BaseModel):
	post_title: str
	post_url: str
	num_comments: int
	hours_since_post: int

class Posts(BaseModel):
	posts: List[Post]


controller = Controller(output_model=Posts)



# 配置无头浏览器（全局共享）
browser_config = BrowserConfig(
    headless=True,  # 关键：启用无头模式
    timeout=60 * 1000,  # 超时时间（毫秒）
    slow_mo=200  # 可选：减缓操作速度（调试时可设为0）
)




# Initialize the model
llm = ChatOpenAI(
	model='gpt-4o-mini',
)


browser_session = BrowserSession(
  browser_profile=BrowserProfile(
    keep_alive=True,
    user_data_dir=None,
    headless=True,
  )
)

task = 'Find the founders of browser-use'
agent = Agent(task=task, llm=llm, browser_session=browser_session, config=browser_config)


async def main():
	
  await browser_session.start()
	
  history = await agent.run()
  
  result = history.final_result()
 
  if result:
    parsed: Posts = Posts.model_validate_json(result)
    
    for post in parsed.posts:
      print('\n--------------------------------')
      print(f'Title:            {post.post_title}')
      print(f'URL:              {post.post_url}')
      print(f'Comments:         {post.num_comments}')
      print(f'Hours since post: {post.hours_since_post}')
	else:
		print('No result')


if __name__ == '__main__':
	asyncio.run(main())
