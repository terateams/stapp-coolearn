def run_app():
    import subprocess, os
    subprocess.call(["streamlit", "run",  os.path.join(os.path.dirname(__file__), "coollearn.py")])
