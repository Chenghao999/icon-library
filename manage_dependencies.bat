@echo off

REM 图标管理器依赖管理工具
echo ==========================================
echo 图标管理器依赖管理工具
echo ==========================================
echo.

echo [1] 检查Python环境...
python --version 2>nul || (echo 错误：未找到Python环境，请先安装Python 3.6+ && pause && exit /b 1)

REM 创建requirements目录
mkdir requirements 2>nul

REM 创建不同级别的依赖文件
echo [2] 创建依赖配置文件...

REM 基础依赖（最小运行要求）
echo Flask>=2.0.0 > requirements\base.txt

REM 完整依赖（包含所有功能）
echo Flask>=3.0.0 > requirements\full.txt
echo pymongo>=4.5.0 >> requirements\full.txt
echo pandas>=2.1.0 >> requirements\full.txt
echo Pillow>=10.0.0 >> requirements\full.txt
echo python-dotenv>=1.0.0 >> requirements\full.txt
echo gunicorn>=21.0.0 >> requirements\full.txt
echo Flask-SQLAlchemy>=3.1.0 >> requirements\full.txt
echo Flask-WTF>=1.2.0 >> requirements\full.txt
echo Flask-CORS>=4.0.0 >> requirements\full.txt

REM 生产环境依赖
echo -r full.txt > requirements\production.txt

:MENU
echo.
echo ========== 依赖管理菜单 ==========
echo [1] 安装基础依赖（最小功能）
echo [2] 安装完整依赖（全部功能）
echo [3] 安装生产环境依赖
echo [4] 检查当前依赖状态
echo [5] 创建离线依赖包（用于无网络环境）
echo [6] 退出
echo.

set /p CHOICE=请选择操作 [1-6]: 

if "%CHOICE%"=="1" (
    echo 正在安装基础依赖...
    pip install -r requirements\base.txt --no-index --find-links=wheels 2>nul || pip install -r requirements\base.txt
    echo 基础依赖安装完成！程序将以最小功能模式运行。
    goto END
) else if "%CHOICE%"=="2" (
    echo 正在安装完整依赖...
    pip install -r requirements\full.txt --no-index --find-links=wheels 2>nul || pip install -r requirements\full.txt
    echo 完整依赖安装完成！所有功能已启用。
    goto END
) else if "%CHOICE%"=="3" (
    echo 正在安装生产环境依赖...
    pip install -r requirements\production.txt --no-index --find-links=wheels 2>nul || pip install -r requirements\production.txt
    echo 生产环境依赖安装完成！
    goto END
) else if "%CHOICE%"=="4" (
    echo 正在检查依赖状态...
    python -c "
import pkg_resources
print('\n已安装的依赖：')
try:
    with open('requirements/full.txt', 'r') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and not line.startswith('-r'):
                try:
                    pkg_resources.require(line)
                    print(f'✓ {line}')
                except Exception as e:
                    print(f'✗ {line} - {e}')
except FileNotFoundError:
    print('无法找到依赖配置文件')
    "
    goto MENU
) else if "%CHOICE%"=="5" (
    echo 正在创建离线依赖包...
    mkdir wheels 2>nul
    pip wheel -r requirements\full.txt -w wheels
    echo 离线依赖包创建完成！
    echo 将wheels目录和requirements目录复制到目标机器即可离线安装。
    goto END
) else if "%CHOICE%"=="6" (
    goto END
) else (
    echo 无效选择，请重新输入！
    goto MENU
)

:END
echo.
echo ==========================================
echo 操作完成！按任意键退出...
pause >nul