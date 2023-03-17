import os.path
from configparser import ConfigParser
from utils.WxError import WxError


class Conf:
    def __init__(self, path: str):
        self.path = path
        self.checkDir()
        self.conf = ConfigParser()
        self.conf.read(path, 'utf-8')
        self.rules = {
            'officials': '公众号名称',
            'price': '出价',
            'budget': '一键起量预算',
            'title': '创意文案',
            'count': '每个账号创建广告的数量',
            'material_count': '单个广告素材的数量'
        }
    
    def getOfficials(self):
        officialStr = self.conf.get('conf', 'officials')
        if len(officialStr) == 0:
            raise WxError('公众号名称配置错误')
        
        if officialStr.count(',') == 0:
            officials = [officialStr]
        else:
            officials = officialStr.split(',')
        
        for name in officials:
            if name == '':
                officials.remove(name)
        
        return officials
    
    def getConfigs(self):
        configs = {}
        for name in self.conf.options('conf'):
            value = self.conf.get('conf', name)
            if value == '':
                raise WxError(self.rules[name] + '配置错误')
            configs[name] = self.getOfficials() if name == 'officials' else value
        
        officials = {}
        for name in configs['officials']:
            officials[name] = {
                'count': int(configs['count']),  # 创建计划的数量
                'material': True,  # 是否上传素材、
            }
        configs['officials'] = officials
        configs['material_num'] = len(os.listdir('conf/images'))
        
        return configs
    
    def checkDir(self):
        if not os.path.exists(self.path):
            raise WxError('配置文件不存在')
        if not os.path.exists('conf/腾讯广告已选择地域定向导出信息.txt'):
            raise WxError('地域定向文件不存在')
        if not os.path.exists('conf/images'):
            raise WxError('素材文件夹不存在')
        if not os.path.exists('auth'):
            os.mkdir('auth')
        if not os.path.exists('logs'):
            os.mkdir('logs')
