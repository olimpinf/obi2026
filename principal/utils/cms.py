import os
from principal.models import PJ, P1, P2, PS
from obi.settings import DEBUG

DEBUG=False

##################################
#### functions for CMS integration

def cms_add_user(compet, compet_type, contest_id):
    CMD = '''ssh -T olimpinf@{} <<'EOF'
cmsAddUser -H '{}' --pbkdf2 '{}' '{}' {}
cmsAddParticipation -H '{}' --pbkdf2 -c {} {}
EOF'''
    if DEBUG:
        host = {PJ: '192.168.0.64', P1: '192.168.0.65', P2: '143.106.73.75', PS: '192.168.0.78'}
    else:
        host = {PJ: 'pj.provas.ic.unicamp.br', P1: '192.168.0.65', P2: '192.168.0.75', PS: '192.168.0.78'}
    password = compet.user.password
    cmd = CMD.format(host[compet_type], password, compet.user.first_name, compet.user.last_name, compet.user.username, password, contest_id, compet.user.username)
    try:
        print(cmd)
        os.system(cmd)
        return 1
    except:
        return 0

def cms_update_password(compet, contest_id):
    CMD = '''ssh -T olimpinf@{} <<'EOF'
cmsUpdatePassword -H '{}' --pbkdf2 {}
EOF'''
    if DEBUG:
        host = {PJ: '192.168.0.64', P1: '192.168.0.65', P2: '143.106.73.75', PS: '192.168.0.78'}
    else:
        host = {PJ: '192.168.0.64', P1: '192.168.0.65', P2: '192.168.0.75', PS: '192.168.0.78'}
    password = compet.user.password
    cmd = CMD.format(host[compet.compet_type], password, compet.user.username)
    try:
        print(cmd)
        os.system(cmd)
        return 1
    except:
        return 0

def cms_remove_user(compet):
    CMD = '''ssh -T olimpinf@{} <<'EOF'
cmsRemoveUser {}
EOF'''
    if DEBUG:
        host = {PJ: '192.168.0.64', P1: '192.168.0.65', P2: '143.106.73.75', PS: '192.168.0.78'}
    else:
        host = {PJ: '192.168.0.64', P1: '192.168.0.65', P2: '192.168.0.75', PS: '192.168.0.78'}
    cmd = CMD.format(host[compet.compet_type], compet.user.username)
    try:
        print(cmd)
        os.system(cmd)
        return 1
    except:
        return 0

