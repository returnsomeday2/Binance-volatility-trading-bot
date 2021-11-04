import json
from datetime import datetime, timedelta

profile_summary_py_file_name = "profile_summary.json"


def notify_bot_pause(user_data_path, flag, TIME_TO_WAIT):
    """

    Args:
        user_data_path:
        flag:
        TIME_TO_WAIT: in minutes
    Returns:

    """

    with open(user_data_path + profile_summary_py_file_name) as f:
        profile_summary = json.load(f)
    profile_summary['bot_paused'] = flag
    market_next_check_time = datetime.now() + timedelta(minutes=TIME_TO_WAIT)
    profile_summary['market_next_check_time'] = str(market_next_check_time)

    with open(user_data_path + profile_summary_py_file_name, 'w') as f:
        json.dump(profile_summary, f, indent=4)

    try:
        with open('UI/update_UI.py', "r") as fp:
            update = int(fp.read().split('=')[1])
    except:
        update = 0

    with open('UI/update_UI.py', "w") as fp:
        fp.write(f"update={update + 1}")

