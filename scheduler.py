"""
Job Application Scheduler

Schedules automatic job application runs at specific times.
Can be used with Windows Task Scheduler or cron on Linux/Mac.
"""
import subprocess
import sys
from datetime import datetime, time
import time as time_module
from pathlib import Path


def run_job_automation():
    """Run the job application automation."""
    print(f"\n{'='*60}")
    print(f"Starting scheduled job application run")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*60}\n")
    
    try:
        # Run naukri_apply.py
        result = subprocess.run(
            [sys.executable, "naukri_apply.py"],
            cwd=Path(__file__).parent,
            capture_output=True,
            text=True,
        )
        
        print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)
        
        print(f"\n{'='*60}")
        print(f"Scheduled run completed at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Exit code: {result.returncode}")
        print(f"{'='*60}\n")
        
        return result.returncode == 0
        
    except Exception as e:
        print(f"Error running automation: {e}")
        return False


def run_at_specific_times(scheduled_times: list[time]):
    """
    Run automation at specific times daily.
    
    Args:
        scheduled_times: List of time objects (e.g., [time(9, 0), time(14, 0), time(18, 0)])
    """
    print(f"Scheduler started. Will run at: {', '.join([t.strftime('%H:%M') for t in scheduled_times])}")
    print("Press Ctrl+C to stop the scheduler")
    
    last_run_date = None
    
    while True:
        now = datetime.now()
        current_time = now.time()
        current_date = now.date()
        
        # Check if we need to run
        for scheduled_time in scheduled_times:
            # Check if it's the scheduled time (within 1 minute window)
            time_diff = abs((datetime.combine(current_date, current_time) - 
                           datetime.combine(current_date, scheduled_time)).total_seconds())
            
            # Run if within 1 minute window and haven't run today for this time
            if time_diff <= 60 and last_run_date != current_date:
                run_job_automation()
                last_run_date = current_date
                break
        
        # Sleep for 30 seconds before checking again
        time_module.sleep(30)


def run_once_after_delay(delay_minutes: int):
    """
    Run automation once after a delay.
    
    Args:
        delay_minutes: Delay in minutes before running
    """
    print(f"Scheduler will run automation in {delay_minutes} minutes")
    print(f"Estimated run time: {(datetime.now().timestamp() + delay_minutes * 60):.0f}")
    
    time_module.sleep(delay_minutes * 60)
    run_job_automation()


def run_with_interval(interval_minutes: int, max_runs: int = None):
    """
    Run automation repeatedly at fixed intervals.
    
    Args:
        interval_minutes: Interval between runs in minutes
        max_runs: Maximum number of runs (None for infinite)
    """
    print(f"Scheduler will run automation every {interval_minutes} minutes")
    if max_runs:
        print(f"Maximum runs: {max_runs}")
    print("Press Ctrl+C to stop")
    
    run_count = 0
    
    while True:
        if max_runs and run_count >= max_runs:
            print(f"Reached maximum runs ({max_runs}). Stopping scheduler.")
            break
        
        run_job_automation()
        run_count += 1
        
        if max_runs and run_count >= max_runs:
            break
        
        print(f"Next run in {interval_minutes} minutes...")
        time_module.sleep(interval_minutes * 60)


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Job Application Scheduler")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Run once command
    parser_once = subparsers.add_parser("once", help="Run automation once immediately")
    
    # Run after delay command
    parser_delay = subparsers.add_parser("delay", help="Run automation after a delay")
    parser_delay.add_argument("--minutes", type=int, required=True, 
                            help="Delay in minutes before running")
    
    # Run at specific times command
    parser_times = subparsers.add_parser("times", help="Run at specific times daily")
    parser_times.add_argument("--times", type=str, required=True,
                            help="Comma-separated times in HH:MM format (e.g., '09:00,14:00,18:00')")
    
    # Run with interval command
    parser_interval = subparsers.add_parser("interval", help="Run at fixed intervals")
    parser_interval.add_argument("--minutes", type=int, required=True,
                               help="Interval between runs in minutes")
    parser_interval.add_argument("--max-runs", type=int, default=None,
                               help="Maximum number of runs (optional)")
    
    args = parser.parse_args()
    
    if args.command == "once":
        run_job_automation()
    elif args.command == "delay":
        run_once_after_delay(args.minutes)
    elif args.command == "times":
        times = [datetime.strptime(t.strip(), "%H:%M").time() 
                for t in args.times.split(",")]
        run_at_specific_times(times)
    elif args.command == "interval":
        run_with_interval(args.minutes, args.max_runs)
    else:
        parser.print_help()
