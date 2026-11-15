"""Run a command with local .env credentials; never prints them."""
import os,sys
from environment import load_environment
load_environment()
if len(sys.argv)<2:raise SystemExit('Usage: python src/with_env.py <command> [args...]')
os.execvpe(sys.argv[1],sys.argv[1:],os.environ)
