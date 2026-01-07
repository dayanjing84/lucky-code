@echo off
chcp 65001 >nul
echo ================================
echo 吉祥号码海报自动发送系统
echo ================================
echo.
echo 启动定时任务...
echo 每天12点和18点自动生成并发送到微信
echo.
echo 按 Ctrl+C 停止程序
echo.
python main.py --schedule
pause
