"""配置管理模块

负责 config.ini 的读取、写入和默认值维护。
配置文件在首次启动时自动生成，缺失的配置项会自动补全。
"""
import configparser
from pathlib import Path

# 项目根目录（main.py 所在目录）
BASE_DIR = Path(__file__).resolve().parent.parent

# 配置文件路径
CONFIG_PATH = BASE_DIR / 'config.ini'

# 浏览器隔离数据目录（pywebview 的 storage_path）
USER_DATA_DIR = BASE_DIR / 'browser_data'

# 默认配置项：(section, key) → default_value
DEFAULTS = {
    ('general', 'translate_url'): 'https://fanyi.baidu.com/mtpe-individual/transText#/',
    ('general', 'window_on_top'): 'true',
    ('general', 'window_width'): '1100',
    ('general', 'window_height'): '750',
    ('general', 'btn_home_x'): '10',
    ('general', 'btn_home_y'): '10',
    ('general', 'btn_top_x'): '10',
    ('general', 'btn_top_y'): '50',
}


def ensure_config() -> configparser.ConfigParser:
    """确保配置文件存在且完整

    - 若 config.ini 不存在则自动创建
    - 若已存在但缺少某些配置项，自动补全缺失项
    - 返回完整的 ConfigParser 对象
    """
    cfg = configparser.ConfigParser()
    if CONFIG_PATH.exists():
        cfg.read(str(CONFIG_PATH), encoding='utf-8')
    changed = False
    for section, key in DEFAULTS:
        if not cfg.has_section(section):
            cfg.add_section(section)
            changed = True
        if not cfg.has_option(section, key):
            cfg.set(section, key, DEFAULTS[(section, key)])
            changed = True
    if changed:
        _save_config(cfg)
    return cfg


def load() -> dict:
    """读取所有配置项并返回字典

    数值型配置项（窗口尺寸、按钮位置）自动转为 int，
    布尔型配置项（置顶状态）自动转为 bool。
    """
    cfg = ensure_config()
    return {
        'translate_url': cfg.get('general', 'translate_url'),
        'window_on_top': cfg.getboolean('general', 'window_on_top'),
        'window_width': cfg.getint('general', 'window_width'),
        'window_height': cfg.getint('general', 'window_height'),
        'btn_home_x': cfg.getint('general', 'btn_home_x'),
        'btn_home_y': cfg.getint('general', 'btn_home_y'),
        'btn_top_x': cfg.getint('general', 'btn_top_x'),
        'btn_top_y': cfg.getint('general', 'btn_top_y'),
    }


def save(key: str, value: str):
    """保存单个配置项到 config.ini

    Args:
        key: 配置项名称（如 'window_on_top'、'btn_home_x'）
        value: 配置项值（字符串形式，写入前需调用方自行转换）
    """
    cfg = configparser.ConfigParser()
    cfg.read(str(CONFIG_PATH), encoding='utf-8')
    if not cfg.has_section('general'):
        cfg.add_section('general')
    cfg.set('general', key, value)
    _save_config(cfg)


def _save_config(cfg: configparser.ConfigParser):
    """将 ConfigParser 对象写入 config.ini 文件"""
    with open(str(CONFIG_PATH), 'w', encoding='utf-8') as f:
        cfg.write(f)
