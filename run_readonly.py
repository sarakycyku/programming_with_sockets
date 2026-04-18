"""Convenience launcher -- run from project root: python run_readonly.py"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from client.readonly_client import ReadOnlyClient
ReadOnlyClient().run_interactive()
