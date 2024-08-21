import os 
from starlette.config import Config
secret_config = Config("dialogtree_phonebot/.env")
# openai_key=secret_config('SECRETKEY')
# org_id=secret_config('ORGID')
