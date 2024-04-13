import yaml
import datetime
from pypushdeer import PushDeer
import sys

proxy_count = 0

def read_config(file_path):
    """读取YAML配置文件"""
    with open(file_path, 'r') as file:
        return yaml.safe_load(file)

def write_config(config, file_path):
    """将配置写入YAML文件"""
    with open(file_path, 'w') as file:
        yaml.dump(config, file)

def update_clash_config(original_config_path, updated_config_path):
    global proxy_count

    # 读取现有的Clash配置
    config = read_config(original_config_path)

    # 从现有配置中提取代理列表
    proxy_names = [proxy['name'] for proxy in config.get('proxies', [])]
    proxy_count = len(proxy_names)

    # 构建proxy-groups
    config['proxy-groups'] = [
        {
            'name': 'Auto',
            'type': 'url-test',
            'proxies': proxy_names,
            'url': 'http://www.gstatic.com/generate_204',
            'interval': 300
        },
        {
            'name': 'Proxy',
            'type': 'select',
            'proxies': ['Auto'] + proxy_names + ['DIRECT']
        },
        {
            'name': 'Domestic',
            'type': 'select',
            'proxies': ['DIRECT', 'Proxy']
        },
        {
            'name': 'Others',
            'type': 'select',
            'proxies': ['Proxy', 'DIRECT']
        }
    ]

    # 添加rules
    config['rules'] = [
        # 广告屏蔽
        'DOMAIN-SUFFIX,ad.com,REJECT',
        'DOMAIN-SUFFIX,ads.com,REJECT',

        # 海外媒体
        'DOMAIN-SUFFIX,netflix.com,Proxy',
        'DOMAIN-SUFFIX,bbc.co.uk,Proxy',
        'DOMAIN-SUFFIX,hulu.com,Proxy',
        'DOMAIN-SUFFIX,youtube.com,Proxy',

        # 中国大陆媒体
        'DOMAIN-SUFFIX,youku.com,Domestic',
        'DOMAIN-SUFFIX,iqiyi.com,Domestic',
        'DOMAIN-SUFFIX,bilibili.com,Domestic',

        # 社交网络
        'DOMAIN-SUFFIX,facebook.com,Proxy',
        'DOMAIN-SUFFIX,twitter.com,Proxy',
        'DOMAIN-SUFFIX,instagram.com,Proxy',
        'DOMAIN-SUFFIX,eu,org,Proxy',

        # 科技公司
        'DOMAIN-SUFFIX,google.com,Proxy',
        'DOMAIN-SUFFIX,github.com,Proxy',
        'DOMAIN-SUFFIX,amazon.com,Proxy',

        # 直连规则
        'DOMAIN-SUFFIX,cn,DIRECT',
        'DOMAIN-KEYWORD,-cn,DIRECT',

        # 默认规则
        'MATCH,Others'
    ]


    # 保存更新后的配置
    write_config(config, updated_config_path)

def push_to_deer(key):
    now = datetime.datetime.now()
    formatted_now = now.strftime("%Y-%m-%d %H:%M:%S")

    title = "## Github机场订阅更新信息"
    msg = "时间： " + formatted_now + " \n更新订阅数量为 " + str(proxy_count)
    print(msg)
    pushdeer = PushDeer(pushkey=key)
    pushdeer.send_markdown(title, desp=msg)

# 使用示例
original_config_path = '../proxies.yaml'
updated_config_path = '../proxies.yaml'
update_clash_config(original_config_path, updated_config_path)
secret_key = sys.argv[1]
push_to_deer(secret_key)
