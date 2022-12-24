from datetime import datetime, timedelta
from textwrap import dedent
import time
# The DAG object; we'll need this to instantiate a DAG
from airflow import DAG
# Operators; we need this to operate!
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator
# These args will get passed on to each operator
# You can override them on a per-task basis during operator initialization

############################################
# DEFINE AIRFLOW DAG (SETTINGS + SCHEDULE)
############################################
default_args = {
    'owner': 'runfeng',
    'depends_on_past': False,
    'email': ['rh3058@columbia.edu'],
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(seconds=30),
    # 'queue': 'bash_queue',
    # 'pool': 'backfill',
    # 'priority_weight': 10,
    # 'end_date': datetime(2016, 1, 1),
    # 'wait_for_downstream': False,
    # 'dag': dag,
    # 'sla': timedelta(hours=2),
    # 'execution_timeout': timedelta(seconds=300),
    # 'on_failure_callback': some_function,
    # 'on_success_callback': some_other_function,
    # 'on_retry_callback': another_function,
    # 'sla_miss_callback': yet_another_function,
    # 'trigger_rule': 'all_success'
}
with DAG(
    'hardware_mon',
    default_args=default_args,
    description='A simple homework DAG',
    schedule_interval='*/1 * * * *',
    start_date=datetime(2022, 11, 1),
    catchup=False,
    tags=['example'],
) as dag:

##########################################
# DEFINE AIRFLOW OPERATORS
##########################################
    # t* examples of tasks created by instantiating operators
    t1 = BashOperator(
        task_id='log_grabber',
        bash_command='python "/home/rh/project/log_grabber.py"',
        retries=1,
    )
    t2 = BashOperator(
        task_id='data_preprocess',
        bash_command='python "/home/rh/project/data_preprocess.py"',
        retries=1,
    )
    t3 = BashOperator(
        task_id='data_process',
        bash_command='python "/home/rh/project/data_process.py"',
        retries=1,
    )


##########################################
# DEFINE TASKS HIERARCHY
##########################################

    # task dependencies 

    t1 >> t2
    t2 >> t3

