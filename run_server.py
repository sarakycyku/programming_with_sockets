"""Convenience launcher -- run from project root: python run_server.py"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from server.tcp_server import main
main()
