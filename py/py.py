from apscheduler.schedulers.background import BackgroundScheduler
import time
import subprocess

def run_job(pathtoscript, *args):
    try:
        cmd = ["python", pathtoscript] + list(args)

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True
        )

        print("Output:", result.stdout)
        print("Errors:", result.stderr)

    except subprocess.CalledProcessError as e:
        print("Job failed:", e.stderr)

def start_scheduler():
    scheduler = BackgroundScheduler()
    scheduler.add_job(lambda: run_job("/app/j.py", "euromilhoes"), 'cron', day_of_week='wed,sat', hour=9, minute=0)
    scheduler.add_job(lambda: run_job("/app/j.py", "totolotoN"), 'cron', day_of_week='thu,sun', hour=9, minute=0)
    scheduler.add_job(lambda: run_job("/app/j.py", "EuroDreams"), 'cron', day_of_week='tue,fri', hour=9, minute=0)
    scheduler.start()
    return scheduler


if __name__ == '__main__':
    scheduler = start_scheduler()
    try:
        while True:
            time.sleep(60)
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()