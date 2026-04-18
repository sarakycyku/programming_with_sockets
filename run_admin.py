"""Convenience launcher -- run from project root: python run_admin.py"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from client.admin_client import AdminClient
AdminClient().run_interactive()
