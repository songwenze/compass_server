import random
import threading
import time
import traceback

import mysql.connector

import twocaptcha_solver
from conf import MYSQL_CONF


def get_mysql_connect():
    return mysql.connector.connect(
        **MYSQL_CONF
    )

def new_task(channel_id, mydb):
    mycursor = mydb.cursor()
    sql = "INSERT INTO `compass`.`youtube_email_task` (`channel_id`) values" \
          " (%s)"
    mycursor.execute(sql, (channel_id,))
    mydb.commit()

def query_task(channel_id, mydb):
    mycursor = mydb.cursor()
    sql = '''select 1 FROM compass.youtube_email_task where channel_id = %s'''
    mycursor.execute(sql, [channel_id])

    res = mycursor.fetchall()

    if len(res) > 0:
        return res[0][0]
    else:
        return None

def query_task_todo(mydb):
    mycursor = mydb.cursor()
    sql = '''select channel_id from compass.youtube_email_task where task_status = 'wait' order by id desc limit 10;'''
    mycursor.execute(sql)

    res = mycursor.fetchall()

    return [e[0] for e in res]



def run_task(channel_id, mydb):
    mycursor = mydb.cursor()
    sql = "UPDATE compass.youtube_email_task set task_status = 'doing' where channel_id = %s and task_status = 'wait'"
    mycursor.execute(sql, (channel_id,))
    mydb.commit()
    if mycursor.rowcount == 1:
        return True
    else:
        return False

def done_task(channel_id, mydb):
    mycursor = mydb.cursor()
    sql = "UPDATE compass.youtube_email_task set task_status = 'done' where channel_id = %s"
    mycursor.execute(sql, (channel_id,))
    mydb.commit()
    if mycursor.rowcount == 1:
        return True
    else:
        return False

def task_fail(channel_id, mydb):
    mycursor = mydb.cursor()
    sql = "UPDATE `compass`.`youtube_email_task` set failed_times = failed_times + 1, task_status = IF(failed_times <= 4, 'wait', 'faild') where channel_id = %s"
    mycursor.execute(sql, (channel_id,))
    mydb.commit()

def immediately_task_fail(channel_id, mydb):
    mycursor = mydb.cursor()
    sql = "UPDATE `compass`.`youtube_email_task` set task_status = 'faild' where channel_id = %s"
    mycursor.execute(sql, (channel_id,))
    mydb.commit()


def query_mysql(id, mydb):
    mycursor = mydb.cursor()
    sql = '''select email FROM compass.youtube_channel_email where channel_id = %s'''
    mycursor.execute(sql, [id])

    myresult = mycursor.fetchall()
    return myresult

def check_health(mydb):
    mycursor = mydb.cursor()
    sql = '''select count(1) FROM compass.email_record  where create_time > DATE_SUB(NOW(),INTERVAL 15 minute)'''
    mycursor.execute(sql)
    total_count = mycursor.fetchall()[0][0]

    sql = '''select count(1) FROM compass.email_record  where create_time > DATE_SUB(NOW(),INTERVAL 15 minute) and length(email) > 0'''
    mycursor.execute(sql)
    success_count = mycursor.fetchall()[0][0]
    try:
        if total_count > 20 and success_count == 0:
            return True
        return False
    except:
        traceback.print_exc()
        return False

def check_captcha_error(mydb):
    mycursor = mydb.cursor()
    sql = '''select count(1) FROM compass.email_record  where create_time > DATE_SUB(NOW(),INTERVAL 15 minute) and msg = 'recaptcha error' '''
    mycursor.execute(sql)
    error_count = mycursor.fetchall()[0][0]
    sql = '''select count(1) FROM compass.email_record  where create_time > DATE_SUB(NOW(),INTERVAL 15 minute) and length(email) > 0'''
    mycursor.execute(sql)
    success_count = mycursor.fetchall()[0][0]
    try:
        if success_count == 0 and error_count > 10:
            return True

        if error_count > success_count*2:
            return True
        else:
            return False
    except:
        traceback.print_exc()
        return False
def query_email(id, mydb):
    res = query_mysql(id, mydb)
    if len(res) > 0:
        return res[0][0]
    else:
        return None


def save_mysql(val, mydb):
    mycursor = mydb.cursor()
    sql = "INSERT INTO `compass`.`youtube_channel_email` (`channel_id`,`email`, `account`) values" \
          " (%s, %s, %s)"
    mycursor.execute(sql, val)

    mydb.commit()

    print(mycursor.rowcount, "record inserted.")



def query_available_account(mydb):
    mycursor = mydb.cursor()
    sql = '''SELECT account_id FROM compass.youtube_account where account_status = 'ready' '''
    mycursor.execute(sql)
    myresult = mycursor.fetchall()
    return [e[0] for e in myresult]

def accquire_account(account, mydb):
    mycursor = mydb.cursor()
    sql = "UPDATE compass.youtube_account set account_status = 'using' where account_id = %s and account_status = 'ready'"
    mycursor.execute(sql, (account,))
    mydb.commit()
    if mycursor.rowcount == 1:
        return True
    else:
        return False

def return_account(account, mydb):
    mycursor = mydb.cursor()
    sql = "UPDATE compass.youtube_account set account_status = 'ready', fail_count = 0, last_success_time = now()  where account_id = %s"
    mycursor.execute(sql, (account,))
    mydb.commit()
    if mycursor.rowcount == 1:
        return True
    else:
        return False

def fail_account(account, mydb):
    mycursor = mydb.cursor()
    sql = "UPDATE compass.youtube_account set account_status = IF(fail_count <= 5, 'ready', 'cooldown'), fail_count = fail_count + 1, last_fail_time = now()  where account_id = %s"
    mycursor.execute(sql, (account,))
    mydb.commit()
    if mycursor.rowcount == 1:
        return True
    else:
        return False
def cooldown_account(account, mydb):
    mycursor = mydb.cursor()
    sql = "UPDATE compass.youtube_account set account_status = 'cooldown', fail_count = fail_count + 1, last_fail_time = now()  where account_id = %s"
    mycursor.execute(sql, (account,))
    mydb.commit()

def recover_account(mydb):
    mycursor = mydb.cursor()
    sql = "UPDATE compass.youtube_account set account_status = 'ready', fail_count = 0  where account_status = 'cooldown'" \
          "and last_fail_time < DATE_SUB(NOW(),INTERVAL 2 HOUR)"
    mycursor.execute(sql)
    mydb.commit()

def query_all_accounts(mydb):
    mycursor = mydb.cursor()
    sql = '''SELECT * FROM compass.youtube_account;'''
    mycursor.execute(sql)

    myresult = mycursor.fetchall()
    return myresult

def query_inactive_account(mydb):
    mycursor = mydb.cursor()
    sql = '''SELECT distinct account FROM compass.email_record  where msg = 'reach limit' and create_time > DATE_SUB(NOW(),INTERVAL 2 HOUR); '''
    mycursor.execute(sql)

    myresult = mycursor.fetchall()
    return myresult

def insert_record(val, mydb):
    mycursor = mydb.cursor()
    sql = "INSERT INTO `compass`.`email_record` (`channel_id`,`email`,`account`, `msg`) values" \
          " (%s, %s, %s, %s)"
    mycursor.execute(sql, val)

    mydb.commit()

    print(mycursor.rowcount, "record inserted.")


acc_use_map = {}

def work(mydb):
    print("thread start")
    while True:
        #  recently health check
        if check_captcha_error(mydb):
            print("too many captcha error, service problem")
            time.sleep(60 * 5)
            continue

        if check_health(mydb):
            print("no one success task in last 15min, stop for a while")
            time.sleep(60 * 10)
            continue

        account = None
        available_accounts = query_available_account(mydb)
        random.shuffle(available_accounts)
        for account_to_choose in available_accounts:
            if accquire_account(account_to_choose, mydb):
                account = account_to_choose
                break

        if not account:
            print("can not fetch account")
            time.sleep(60 * 5)
            continue

        task_todo_list = query_task_todo(mydb)
        random.shuffle(task_todo_list)
        channel_id = None
        for task_to_choose in task_todo_list:
            if run_task(task_to_choose, mydb):
                channel_id = task_to_choose
                break

        if not channel_id:
            print("no task to do")
            return_account(account, mydb)
            twocaptcha_solver.human_fake_action(account)
            continue




        # account = None
        # for i in range(100):
        #     fetched_account = account_q.get()
        #     if fetched_account in inactive_account_list:
        #         account_q.put(fetched_account)
        #     else:
        #         account = fetched_account
        #         break
        #
        # if not account:
        #     time.sleep(60 * 5)
        #     print("can not fetch account")
        #     continue

        # if account not in acc_use_map:
        #     acc_use_map[account] = 0
        # else:
        #     acc_use_map[account] += 1
        # print(acc_use_map)


        email = None
        reach_limit = False
        captcha_error = False
        channel_error = False

        # processing_task.append(channel_id)
        try:
            email = twocaptcha_solver.main_solve(f'''https://www.youtube.com/channel/{channel_id}/about''', account=account)
        except twocaptcha_solver.ReCaptchaServiceError:
            print('captcha error')
            captcha_error = True
        except twocaptcha_solver.ChannelError:
            channel_error = True
        except Exception as e:
            if 'reached access limit' in str(e):
                print('reached access limit')
                reach_limit = True

        if email is not None and len(email) > 0:
            insert_record((channel_id, email, account, None), mydb)
            save_mysql((channel_id, email, account), mydb)
            done_task(channel_id, mydb)
            return_account(account, mydb)
        else:
            task_fail(channel_id, mydb)
            if reach_limit:
                insert_record((channel_id, None, account, 'reach limit'), mydb)
                cooldown_account(account, mydb)
            elif captcha_error:
                insert_record((channel_id, None, account, 'recaptcha error'), mydb)
                fail_account(account, mydb)
            elif channel_error:
                insert_record((channel_id, None, account, 'channel error'), mydb)
                # channel doesn't exists or present email
                return_account(account, mydb)
                immediately_task_fail(channel_id, mydb)
            else:
                insert_record((channel_id, email, account, None), mydb)
                fail_account(account, mydb)
    mydb.close()




def main():
    thread_num = 1
    threads = []
    for i in range(0, thread_num):
        t = threading.Thread(target=work, args=(get_mysql_connect(),))
        threads.append(t)

    for thread in threads:
        time.sleep(1)
        thread.start()
    for thread in threads:
        time.sleep(1)
        thread.join()


if __name__ == "__main__":
    mydb = get_mysql_connect()
    task_list = ['UCZ3IYWkaf1IpMIitcPgmLVA', 'UC8IbhpQwrTD6BozJPWnyAHA', 'UC3PN16bp92qeSn3kw0VpVEg', 'UC6vOe7JpQecPBvbVcmjcMkw', 'UCgTxjhiS26gKeuBHLakKF2A', 'UCc07T7LZ-6kkitPGuuJmXwg', 'UCEO61QmMhqEgl5UFxL2ka4Q', 'UCE30LRXhZs1KVTTV1IwfNrQ', 'UCj5ajIdsaPntB-r4aYtaz7g', 'UC_EOIX6CoWe8bmMJd8lQFBQ', 'UC_rkANJTrR71ttOZOAqkOtQ', 'UC5WJ5OuP_oV6VQdHxaZi_TQ', 'UCjXOvTlLcntnmtNQQRPtQLg', 'UCFTBnYJjZFiT_znFiGgWpEA', 'UCaGAGzhtubWbUPs9NsdYL4A', 'UCkDKLo1u9XSSWpqvnGkRh1Q', 'UCGNEmQhVBpUVtE1aGB0iysA', 'UCOvElA2Z-oLIitHHLxRu7rw', 'UCMMBvtjwSzWNLH0yz1W38aw', 'UCFS15uIWcSXZ9AqZ-mGxUhA', 'UC_n5O7LhzsqvfWMoDO6JfEw', 'UCkzVo9xAAqT5zrqEJtA1nMw', 'UCnTEspqZ81OavPCSStESeuw', 'UCRxdywlZBu3iEVzTYqK00Eg', 'UCYepXbjcDmPHzl07Y7DxiBg', 'UCK_1aRAYOWhko6vEAxcpYOQ', 'UC8TIr8W10OIuka9EECplOiw', 'UCw_0DgEHXr4ZF_CA2jevfOg', 'UCn-OWwDXgX_xD_5LxJKvCZQ', 'UCTKV7tRsdvXZgW8yFRJkVfw', 'UCa5BHKyrKOuw8zqz8kSY2DA', 'UCWdpOjNxQjqnws4GPtC4Dxw', 'UCd8Vbro7VJzH8s2pzQ5u1JA', 'UC6nkHbnWIrpaDBHXQ_1aiIA', 'UCjXOvTlLcntnmtNQQRPtQLg', 'UC-xpQ4HH7ihWieyKZVznTIg', 'UCvcjgwHemw7SZoYtUE6UodQ', 'UCobcqmUDwT08COK-0rlm2wA', 'UCei5en2_Mqvyj9Cvp9jIODA', 'UCD9j5qyDqQvb9qnLss3vxww', 'UCOta6MHpxOCLIp76wbv5WZw', 'UCO5joC_tejK9kHDoKUGGDGw', 'UC104IJSb0QwNGzG6goH-XcQ', 'UCnm9QfdUZJH5a5sgmJb2z4w', 'UCww5frdabn9GLHA9y6J8d4Q', 'UCQbKY-qMKLZvMuKEhfvnczw', 'UC0XH2CxCQ-oQgzehk6mXwmQ', 'UCa47kUQqXWTNSNAtL2233Qg', 'UCdl34X83KuirjTQXx0hVHSg', 'UCKKpTY3LN_DAp1gP1ATeG0A', 'UC5bH9bk8LqJCHwrpkidhhkQ', 'UCwD07KzE0r9spFjpFx8egDQ', 'UCyWBb9EcWQW0H_madCuKAwg', 'UCOPeHgsubs2K686vF_sPVgQ', 'UCzQIPb2JkYiSLJh0VZXdcZw', 'UCkT2q8AiQOblmgzE4Hhas8w', 'UCWR6BjL6lsxKYMaRnhnRmgw', 'UCPuW3r7l4GK1jdK3hB-P76Q', 'UCdPqoNvCszVJ1YZ4yxob_GA', 'UCu5fhM_kM2ir8T_4ko7KhUA', 'UCgJUD2wML8mMwXSOXgdF2rA', 'UCVK2kyAJVsIc4lOTWJ1loSA', 'UC0tRwUkOZQCPFLmeATR0xHg', 'UCGseAbEqUpDDqSmVFmHd6ug', 'UC6O7FNj9NskCjRwCGEQp5hw', 'UCYghTXIbpowhi0A2r8OwxpQ', 'UCVLdXUVrbqtD3F_ljJ1-2kQ', 'UCholJYdAD8eikL1YFalBAdg', 'UCxTfmlRQWtkdWPgLZusx0ug', 'UC0TaBi9sj73MbRhfYNVV5fA', 'UCcnLQtpZBgT_nW8H6hSJXtw', 'UCdGov5F25aQxbtsmbCxYQLA', 'UCfwMbCgHyJ2COPIqKS5r8Ww', 'UCGEpJm9jBST0cxrA19e_SAw', 'UC7Bu_3OE2lIWhPshtSi3I9g', 'UCXDTMcSsvF_LbepGT68b98w', 'UC3JIxkj4rx9SQcZjKCDYU2w', 'UCW-mYgxd1fT0_GR3typ5IXQ', 'UCd4cMIJtRgSz4xbxb1klIvg', 'UCHVb1TNupwgxu_LXgLEfeMA', 'UCSJidXupxYuxYkCfiXrFHaA', 'UCH5txIWhFMhI7yI_047V3Xw', 'UCiDj9x2tLUNgaXQgefJWikQ', 'UC-luaBAGSqZ---25Wifnnhg', 'UCs3fHsrNLwraD0lQoSW3MSw', 'UC2WX-tmUbt1k6oRYtEu3qBg', 'UCC4TZTTDUnbfhB8fJLPc0iA', 'UC23cXqYTSh7K6tLT3rTwVCA', 'UCT8kywKhwSITanAnurL5L8Q', 'UCR0KQtKteqSkc3-yDU0077g', 'UCqATe4xZNaPgjREiMXA9mLQ', 'UCyVqjUaOZX1WjitGHIZaZAw', 'UCNhbF8r9cU9loMFv_Q4vLPw', 'UCTtyUKxiDWzBPw8t-dNafiA', 'UCgBYW37v8gffq7U_B-p7aDw', 'UCV-ohagoh6SGJ0ScYkVywIg', 'UCeUMQD_XZCTw24Be8crGWDg', 'UCT8kywKhwSITanAnurL5L8Q', 'UCP-t58QjrcYjTnVlVEP2hng', 'UC9k6vp8enGg-2qfEBDK4Fjg', 'UCWhMkbaEKLs0oeMNGJ3jTxw', 'UC22hd9jAWkPYTO5sVlxSSjg', 'UCiKFIiNMcf3TyufD_vPxx0A', 'UCLXPfv5kfYczP_L5rklRRhA', 'UCiKFIiNMcf3TyufD_vPxx0A', 'UCzdt832iuUpVf6I5BfV9-KA', 'UCmd5SB5cb-3BX8c7tzps-QA', 'UC1QOuvOFsf3YvF64ritAoeg', 'UC88BygbplVOdRjROIgohF9A', 'UCZ8426BC1YO4dawJmFQiRmA', 'UCNeyj5uy8jpsh3bPaVwjqxg', 'UCsN3lSTy5lDdiVRZ-LQ3RsQ', 'UC2LKqyVEHlz18BIVUfwEEwg', 'UCLfPpvREdzivJpCk_6tUVqw', 'UCIrsMuYD7L5LM2E580h1QsA']
    for channel_id in task_list:
        if not query_email(channel_id, mydb):
            if not query_task(channel_id, mydb):
                new_task(channel_id, mydb)
                print('inserted')
    mydb.close()
    main()
    # email = twocaptcha_solver.main_solve('https://www.youtube.com/channel/UCJ0w7yV1q0aEuKo_lZ4O5WA/about', account='account91')
