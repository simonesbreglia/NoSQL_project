import subprocess

# esegui il comando streamlit run my_app/app.py --server.port 8501

subprocess.run(["streamlit", "run", "my_app/app.py", "--server.port", "8501"])