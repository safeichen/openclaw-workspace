#!/usr/bin/env python3
"""
检查网络连接和端口访问
"""

import socket
import sys
import subprocess
from datetime import datetime

def check_port(host, port):
    """检查端口是否可访问"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(3)
        result = sock.connect_ex((host, port))
        sock.close()
        return result == 0
    except Exception as e:
        return False

def check_local_server():
    """检查本地服务器"""
    print("🔍 检查本地服务器状态...")
    
    # 检查进程
    try:
        result = subprocess.run(['pgrep', '-f', 'server.py'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("  ✅ Python服务器进程运行中")
            pids = result.stdout.strip().split()
            for pid in pids:
                try:
                    cmd = subprocess.run(['ps', '-p', pid, '-o', 'cmd='], 
                                       capture_output=True, text=True)
                    print(f"    进程 {pid}: {cmd.stdout.strip()}")
                except:
                    pass
        else:
            print("  ❌ Python服务器进程未运行")
    except:
        print("  ⚠️  无法检查进程状态")
    
    # 检查端口监听
    try:
        result = subprocess.run(['netstat', '-tlnp'], 
                              capture_output=True, text=True)
        if ':8081' in result.stdout:
            print("  ✅ 端口 8081 正在监听")
            for line in result.stdout.split('\n'):
                if ':8081' in line:
                    print(f"    监听状态: {line.strip()}")
        else:
            print("  ❌ 端口 8081 未监听")
    except:
        print("  ⚠️  无法检查端口状态")

def check_external_access():
    """检查外部访问"""
    print("\n🌐 检查外部网络访问...")
    
    server_ip = "43.159.52.61"
    port = 8081
    
    print(f"  服务器IP: {server_ip}")
    print(f"  端口: {port}")
    
    # 检查端口访问
    print(f"  检查端口 {port} 访问性...")
    if check_port(server_ip, port):
        print(f"  ✅ 端口 {port} 可访问")
    else:
        print(f"  ❌ 端口 {port} 不可访问")
        print("    可能原因:")
        print("    1. 云服务器安全组未开放端口")
        print("    2. 服务器防火墙阻止了端口")
        print("    3. 服务器未正确绑定到外部接口")
    
    # 测试HTTP连接
    print(f"  测试HTTP连接...")
    try:
        import urllib.request
        import urllib.error
        
        url = f"http://{server_ip}:{port}/api/status"
        req = urllib.request.Request(url)
        
        try:
            response = urllib.request.urlopen(req, timeout=5)
            if response.status == 200:
                print(f"  ✅ HTTP连接成功 (状态码: {response.status})")
                data = response.read().decode('utf-8')
                print(f"    响应: {data[:100]}...")
            else:
                print(f"  ❌ HTTP连接失败 (状态码: {response.status})")
        except urllib.error.URLError as e:
            print(f"  ❌ HTTP连接错误: {e.reason}")
        except Exception as e:
            print(f"  ❌ HTTP连接异常: {str(e)}")
            
    except ImportError:
        print("  ⚠️  无法测试HTTP连接 (缺少urllib)")

def check_firewall():
    """检查防火墙设置"""
    print("\n🔥 检查防火墙设置...")
    
    # 检查firewalld
    try:
        result = subprocess.run(['systemctl', 'status', 'firewalld'], 
                              capture_output=True, text=True)
        if 'active (running)' in result.stdout:
            print("  ⚠️  firewalld 正在运行")
            print("    需要添加规则: firewall-cmd --add-port=8081/tcp --permanent")
            print("    然后重启: firewall-cmd --reload")
        else:
            print("  ✅ firewalld 未运行或已停止")
    except:
        print("  ⚠️  无法检查firewalld状态")
    
    # 检查iptables
    try:
        result = subprocess.run(['iptables', '-L', '-n'], 
                              capture_output=True, text=True)
        if '8081' in result.stdout:
            print("  ⚠️  iptables 可能有8081端口规则")
        else:
            print("  ✅ iptables 未发现8081端口限制")
    except:
        print("  ⚠️  无法检查iptables状态")

def main():
    """主函数"""
    print("=" * 60)
    print("OpenClaw测试页面网络访问诊断")
    print(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    check_local_server()
    check_external_access()
    check_firewall()
    
    print("\n" + "=" * 60)
    print("📋 建议操作:")
    print("1. 登录云服务器控制台")
    print("2. 检查安全组规则，确保8081端口已开放")
    print("3. 如果使用防火墙，添加规则: firewall-cmd --add-port=8081/tcp")
    print("4. 重启服务器: ./start-server.sh restart")
    print("5. 测试访问: curl http://43.159.52.61:8081")
    print("=" * 60)

if __name__ == "__main__":
    main()