import curses
import time
from multiprocessing import Array, Manager, freeze_support

from check_thread import CheckRateLimit, CheckTweet
from select_boss import boss_select_menu
from status_monitor import StatusMonitor
from tweet import RequestFaildError, Tweet
from util import (INTERVAL_PATTERN, MAIN_WIN_HEIGHT, MAIN_WIN_WIDTH,
                  get_user_access_token, setup)


def do_action(key: str, thread: CheckTweet, monitor: StatusMonitor) -> bool:
    if key == "q":
        return False, False
    elif key == "p":
        return False, True
    elif key == "d":
        thread.update_interval(INTERVAL_PATTERN[0])
    elif key == "s":
        thread.update_interval(INTERVAL_PATTERN[1])
    elif key == "a":
        thread.update_interval(INTERVAL_PATTERN[2])
    elif key == "c":
        thread.update_copy_flag(not thread.get_copy_flag())
        monitor.switch_pause_panel(enable_copy=thread.get_copy_flag())
    return True, False


def stop_running_threads(threads: list):
    """stop_running_threads

    実行中のすべてのthreadを止める
    """
    for thread in threads:
        if thread.is_alive():
            # thread.acquire()  # ロックを獲得
            thread.stop()  # フラグを更新
            thread.join()  # 終了待機


def main(stdscr):
    curses.start_color()
    curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_RED, curses.COLOR_BLACK)
    curses.init_pair(3, curses.COLOR_BLACK, curses.COLOR_WHITE)
    curses.init_pair(4, curses.COLOR_WHITE, curses.COLOR_BLACK)
    curses.resize_term(MAIN_WIN_HEIGHT, MAIN_WIN_WIDTH)
    need_more_loop_flag = True

    """
    Twitter APIの"search/tweet"でのRate Limit
    Limit, remain, reset
    """
    ratelimit_statuses = Array("Q", 3)

    while need_more_loop_flag:
        need_more_loop_flag = False
        select = boss_select_menu(stdscr)
        stdscr.clear()
        monitor = StatusMonitor(stdscr, ratelimit_statuses, select)
        check_tweet = CheckTweet(
            search_query=select.get("search_query"), monitor=monitor
        )
        check_rate_linit = CheckRateLimit(statuses=ratelimit_statuses)
        check_tweet.start()
        check_rate_linit.start()
        while True:
            try:
                key = stdscr.getkey()
                exit_flag, need_more_loop_flag = do_action(key, check_tweet, monitor)
                if exit_flag:
                    pass
                else:
                    break
            except:
                pass
        monitor.please_wait_view()
        stop_running_threads((check_tweet,))
        stdscr.clear()


if __name__ == "__main__":
    freeze_support()
    setup()
    try:
        Tweet().get_rate_limits()
    except RequestFaildError:
        get_user_access_token()

    curses.wrapper(main)
