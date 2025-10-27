#!/usr/bin/env python3
"""
VirtPLC Simulator Startup Script

Easy way to start the VirtPLC simulator in different modes.
"""

import argparse
import asyncio
import sys
from pathlib import Path

# Add current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

from main import main

def start_plc_server(host="0.0.0.0", port=8080, opcua_port=4840):
    """Start the simulator as a PLC replacement server"""
    print("🚀 Starting VirtPLC as PLC Replacement Server...")
    print(f"   Web API: http://{host}:{port}")
    print(f"   OPC-UA: opc.tcp://{host}:{opcua_port}/virtplc/")
    print("   Use 'python cli_manager.py' for device management")
    print("   Press Ctrl+C to stop")
    print("-" * 60)
    
    # Set up arguments for main()
    sys.argv = [
        'main.py',
        '--mode', 'plc-server',
        '--host', host,
        '--port', str(port),
        '--opcua-endpoint', f'opc.tcp://{host}:{opcua_port}/virtplc/',
        '--update-interval', '1.0'
    ]
    
    asyncio.run(main())

def start_web_only(host="0.0.0.0", port=8080):
    """Start only the web API"""
    print("🌐 Starting VirtPLC Web API...")
    print(f"   Web API: http://{host}:{port}")
    print("   Press Ctrl+C to stop")
    print("-" * 60)
    
    sys.argv = [
        'main.py',
        '--mode', 'web',
        '--host', host,
        '--port', str(port),
        '--update-interval', '1.0'
    ]
    
    asyncio.run(main())

def start_opcua_only(host="0.0.0.0", port=4840):
    """Start only the OPC-UA server"""
    print("🔌 Starting VirtPLC OPC-UA Server...")
    print(f"   OPC-UA: opc.tcp://{host}:{port}/virtplc/")
    print("   Press Ctrl+C to stop")
    print("-" * 60)
    
    sys.argv = [
        'main.py',
        '--mode', 'opcua',
        '--opcua-endpoint', f'opc.tcp://{host}:{port}/virtplc/',
        '--update-interval', '1.0'
    ]
    
    asyncio.run(main())

def start_interactive():
    """Start interactive CLI"""
    print("💻 Starting VirtPLC Interactive CLI...")
    print("   Type 'help' for available commands")
    print("   Press Ctrl+C to stop")
    print("-" * 60)
    
    sys.argv = [
        'main.py',
        '--mode', 'interactive'
    ]
    
    asyncio.run(main())

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="VirtPLC Simulator Startup Script")
    parser.add_argument("--mode", 
                       choices=["plc-server", "web", "opcua", "interactive"],
                       default="plc-server",
                       help="Startup mode")
    parser.add_argument("--host", default="0.0.0.0", help="Host address")
    parser.add_argument("--port", type=int, default=8080, help="Web API port")
    parser.add_argument("--opcua-port", type=int, default=4840, help="OPC-UA port")
    
    args = parser.parse_args()
    
    try:
        if args.mode == "plc-server":
            start_plc_server(args.host, args.port, args.opcua_port)
        elif args.mode == "web":
            start_web_only(args.host, args.port)
        elif args.mode == "opcua":
            start_opcua_only(args.host, args.opcua_port)
        elif args.mode == "interactive":
            start_interactive()
    except KeyboardInterrupt:
        print("\n👋 Shutting down VirtPLC Simulator...")
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
