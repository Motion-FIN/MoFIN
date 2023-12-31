import torch
from collections import OrderedDict
import torch.nn as nn
from torch.nn.parallel import DistributedDataParallel
from utils.model_profile import make_profile
from functools import partial

def load_weights(model, cfg, begin_with_module=False):
    if hasattr(cfg,'pretrained') and cfg.pretrained != None:
        d = torch.load(cfg.pretrained, map_location='cpu')
        
        if begin_with_module:
            new_d = OrderedDict()
            for k,v in d.items():
                k = k.replace('module.','',1)
                new_d[k] = v
            model.load_state_dict(new_d, True)
        else:
            model.load_state_dict(d, True)
            
        print(f'[{cfg.name}] load pretrained model from "{cfg.pretrained}"')
        return True
    return False

def make_model(cfg, cuda=True):
    if cfg.name== 'MoFIN':
        from .mofin.interpolator import Interpolator as MoFIN
        model = MoFIN(cfg)

        load_weights(model,cfg,begin_with_module=True)

    else:
        raise NotImplementedError

    if cuda:
        return model.cuda()
    else:
        return model
    
def model_profile(cfg):
    
    sz = (256,256)
    inputs=(torch.randn(1,3,*sz).cuda(),
            torch.randn(1,3,*sz).cuda())
    inputs_description = f'(1x3x{sz[0]}x{sz[1]},1x3x{sz[0]}x{sz[1]})'
    
    profile = make_profile(
        model_maker=partial(make_model,cfg),
        inputs=inputs,
        inputs_description=inputs_description)
    
    return profile