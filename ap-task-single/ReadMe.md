创建 auth.json 的方法
方法1：使用 Playwright 命令行（推荐）
# 打开浏览器并在登录后保存状态
playwright open https://ui.appen.com --save-storage=auth.json
playwright open https://jd.com --save-storage=auth.json


# 这会：
# 1. 打开一个浏览器窗口
# 2. 导航到指定网站
# 3. 等待您手动登录
# 4. 关闭浏览器时自动保存所有状态到 auth.json

