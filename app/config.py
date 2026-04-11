"""配置管理"""
import configparser
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
CONFIG_PATH = BASE_DIR / 'config.ini'
USER_DATA_DIR = BASE_DIR / 'browser_data'

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
    """若配置文件不存在则自动生成默认配置，缺失项自动补全"""
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
    """读取所有配置项并返回字典"""
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
    """保存单个配置项"""
    cfg = configparser.ConfigParser()
    cfg.read(str(CONFIG_PATH), encoding='utf-8')
    if not cfg.has_section('general'):
        cfg.add_section('general')
    cfg.set('general', key, value)
    _save_config(cfg)


def _save_config(cfg: configparser.ConfigParser):
    with open(str(CONFIG_PATH), 'w', encoding='utf-8') as f:
        cfg.write(f)
