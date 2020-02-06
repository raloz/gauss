import argparse
import os
import json
import re
import subprocess
import datetime
from shutil import copyfile
from colored import fg, bg, attr
from PyInquirer import style_from_dict, Token, prompt, Separator


# initiate the parser
parser = argparse.ArgumentParser(prog="gauss", description= '{color}Sincroniza tu proyectos dentro de la cuenta NetSUite{reset}'.format(color=fg('cyan'), reset=attr('reset')), formatter_class=argparse.RawTextHelpFormatter)
parser.add_argument("-v", "--version",help="Versión actual del script", action="store_true")
parser.add_argument("-c", "--createproject", nargs="+", help="Crea un nuevo proyecto de tipo ACCOUNTCUSTOMIZATION")
parser.add_argument("-s", "--script", nargs="+", help="Create SuiteScripts 2.0 files in directory [userevent, suitelet, scheduled, client, mapreduce, restlet] \nUSAGE:\nmonitor --scriptfile userevent=file1.js,subfolder/file2.js clientscript=file3.js")
parser.add_argument("-r", "--recordscript", action="store_false", help="")
parser.add_argument("-u", "--upload", nargs="+", help="Load file/folder into FileCabinet")
parser.add_argument("-d", "--deploy", action="store_true", help="Deploy project into NetSuite")

args = parser.parse_args()
# global variables/constants
with open(os.path.join(os.path.dirname(os.path.realpath(__file__)),'config.json'),'r+') as _file:
    config = json.load(_file)
_file.close()

CWD = os.getcwd()
AGREGAR = "===[ AGREGAR NUEVAS CREDENCIALES ]==="
SDFCLI = os.path.join(os.path.dirname(os.path.realpath(__file__)),'sdfcli','sdfcli')
DATETIME = datetime.datetime.now()

def is_project():
    return  True if(os.path.isfile(os.path.join(CWD,'.sdf')) is True) else False
#is_project

def is_required(current):
    return True if(current != '') else False
#is_required

def create_account(project):
    questions = [
        {
            'type': 'input',
            'name': 'name',
            'qmark': '?',
            'message': 'Friendly name account:',
            'validate': is_required 
        },
        {
            'type': 'input',
            'name': 'email',
            'qmark': '?',
            'message': 'Email address:',
            'validate': is_required 
        },
        {
            'type': 'password',
            'name': 'password',
            'qmark': '?',
            'message': 'Password:',
            'validate': is_required 
        },
        {
            'type': 'input',
            'name': 'accountid',
            'qmark': '?',
            'message': 'Enter your company id:',
            'validate': is_required 
        },
    ]
    account = prompt(questions)

    #se salvan las credenciales en el archivo JSON
    with open(os.path.join(os.path.dirname(os.path.realpath(__file__)),'config.json'),'r+') as _file:
        config['credentials'][account["name"]] = {
                "email": account["email"],
                "password": account["password"],
                "accountid": account["accountid"],
                "url": "system.netsuite.com",
                "role": 3
            }

        cp = config['credentials'][AGREGAR]
        config["credentials"].pop(AGREGAR)
        config["credentials"][AGREGAR] = cp

        json.dump(config, _file, indent=4, sort_keys=False)
    _file.close()
    subprocess.call(['python', os.path.join(os.path.dirname(os.path.realpath(__file__)),'gauss.py'),'--createproject', project],shell=True)
#create_account

def create_script_record():
    command = arg.split('=')
    _script_type = command[0] 
    _file = command[1].split(os.path.sep)[-1]
    _subdir = command[1].replace(_file,'')

    if(os.path.isfile(os.path.join(CWD,'FileCabinet','SuiteScripts',_subdir,_file))):
        with open(os.path.join(os.path.dirname(os.path.realpath(__file__)),'objects','{}.xml'.format(_script_type)), 'r+') as _template:
            template = _template.read()
        _template.close()
        _choose = [
            {
                'type': 'input',
                'name': 'name',
                'qmark': '?',
                'message': 'Nombre del record script:',
                'validate': is_required 
            }
        ]
        name = prompt(_choose)
        #create customscript xml file
        with open(os.path.join(CWD,'Objects','customscript_{}'.format(_file.replace('.js','.xml'))),'w+') as file:
            file.write(template.format(scriptid='customscript_{}'.format(_file.replace('.js','')),name=name['name'],file=os.path.join(_subdir,_file),deploy=_file.replace('.js','')))
        file.close()
    else:
        print("""{color}Error: El archivo de referencia no existe{reset}""".format(color=fg('yellow'), reset=attr('reset'))) 
        exit()
#create_script_record

def get_jsfiles():
    path = os.path.join(CWD,'FileCabinet','SuiteScripts')
    files = []
    # r=root, d=directories, f = files
    for r, d, f in os.walk(path):
        for file in f:
            if '.js' in file:
                files.append(os.path.join(r, file))

    return files
#get_jsfiles

def record_in(file_path):
    dirty = "(type|:|.*\.Type\.|\\\")"
    search = [config['record'][record]['regex'] for record in config['record'] if 'regex' in config['record'][record]]
    with open(file_path,'r+') as current:
        lines = current.readlines()
        current.close()
    #all matches from general regex
    match = [x.strip() for x in lines if any(re.search(r,x) for r in search)]
    result = {}
    #get type, record id from all record used in js file
    for record in config['record']:
        search = ["{},".format(config['record'][record]['netsuite']),"{}\"".format(config['record'][record]['id'] if 'id' in config['record'][record] else '--')]
        inlist = [y.strip() for y in match if any(re.search(s,y) for s in search)]
        if len(inlist) > 0:
            for item in inlist:
                _recordid = re.sub(dirty, '', item)
                _recordid = re.sub(('[//",\']'), '', _recordid)
                #_recordid = re.sub(('\_'), ' ', _recordid)
                try:
                    if _recordid.lower().strip() not in result[config['record'][record]['category'] if 'category' in config['record'][record] else 'Other']: 
                        result[config['record'][record]['category'] if 'category' in config['record'][record] else 'Other'].append(_recordid.lower().strip())
                except:
                    result[config['record'][record]['category'] if 'category' in config['record'][record] else 'Other'] = [_recordid.lower().strip()]
    
    return result
#create_records_log

def error_in_log():
    _log = []
    _marktime = DATETIME.timestamp()
    if(os.path.isfile(os.path.join(CWD,'error.log'))):
        with open(os.path.join(CWD,'error.log')) as log:
            lines = log.readlines()
            lines.reverse()
            log.close()
        #search for mark of time
        for line in lines:
            if(re.match('\d{4}\-\d{2}\-\d{2}', line)):
                if datetime.datetime.fromisoformat(line[:19]).timestamp() >= _marktime:
                    _log.append(line)
    return _log
#error_in_log

#============== check for --version or -V ==============
if args.version:
    print("""{color}Sincroniza tu proyectos dentro de la cuenta NetSUite{reset}""".format(color=fg('yellow'), reset=attr('reset')))

#============== create a new project --createproject or -p ==============
if args.createproject is not None:
    _project = args.createproject[0]
    questions = [
        {
            'type': 'list',
            'name': 'account',
            'qmark': '?',
            'message': 'Selecciona una cuenta o agrega una nueva para el proyecto:',
            'choices': [account for account in config["credentials"]]
        }
    ]
    answers = prompt(questions)
    if answers["account"] != AGREGAR:
        if(os.path.isdir(os.path.join(CWD,_project)) == False):
            #create project from sdfcli NetSuite
            subprocess.call([SDFCLI,'createproject', '-type', 'ACCOUNTCUSTOMIZATION', '-parentdirectory', CWD, '-projectname', _project],shell=True)
            #add all dependencies to manifest.xml
            subprocess.call([SDFCLI,'adddependencies', '-feature', 'SERVERSIDESCRIPTING:required','CUSTOMRECORDS:required', '-project', _project], shell=True)
            #create .SDF file for this project
            with open(os.path.join(CWD,_project,'.sdf'),'w+') as file:
                file.write("account={}\nemail={}\nrole=3\nurl=system.netsuite.com\npass={}".format(config['credentials'][answers["account"]]['accountid'],config['credentials'][answers["account"]]['email'],config['credentials'][answers["account"]]['password']))
            file.close()
            #git commands for this project
            subprocess.call(['git','init', os.path.join(CWD,_project) ],shell=True)
            #create gitignore file for this project
            with open(os.path.join(CWD,_project,'.gitignore'),'w+') as file:
                file.write(".sdf\n**/error.log\n")
            file.close()
        else:
            print("""{color}Error: No se puede duplicar el nombre de un mismo proyecto{reset}""".format(color=fg('yellow'), reset=attr('reset'))) 
    else:
        create_account(args.createproject[0])

#============== create a new suitescript file ==============
if args.script is not None:
    if(is_project()):
        for arg in args.script:
            command = arg.split('=')
            _file = command[1].split(os.path.sep)[-1] 
            _subdir = command[1].replace(_file,'')
            with open(os.path.join(CWD,'.sdf'),'r+') as file:
                _line = file.readlines()
            _line = _line[1].split('=')
            _email = _line[1].strip()
            file.close()

            if _subdir != '':
                os.makedirs(os.path.join(CWD,'FileCabinet','SuiteScripts',_subdir), exist_ok=True)

            with open(os.path.join(os.path.dirname(os.path.realpath(__file__)),'.template'), 'r+') as _template:
                template = _template.read()
            _template.close()
            _choose = [
                {
                    'type': 'checkbox',
                    'qmark': '?',
                    'name': 'entry_point',
                    'message': "Selecciona los Entry Points para tu {} script:".format(command[0]),
                    'choices': [dict([("name",entry)]) for entry in config["script_types"][command[0]]["entry_points"]]
                }
            ]
            entry_point = prompt(_choose)
            entry_point = ["{func}: function(){{\n\n\t\t}},".format(func=function) for function in entry_point['entry_point']]

            copyfile(os.path.join(os.path.dirname(os.path.realpath(__file__)),'.template'),os.path.join(CWD,'FileCabinet','SuiteScripts',_subdir,_file))
            #se crea el archivo js
            with open(os.path.join(CWD,'FileCabinet','SuiteScripts',_subdir,_file),'w+') as file:
               file.write(template.format(author=_email, script_type=config["script_types"][command[0]]["name"], entry_point='\n\t\t'.join(entry_point), script_name=_file))
            file.close()
            #se crea el record script
            if args.recordscript:
                create_script_record()
    else:
        print("""{color}Error: El comando solo puede ejecutarse dentro de un proyecto{reset}""".format(color=fg('yellow'), reset=attr('reset'))) 
        exit()

#============== upload file/folder into FileCabinet ==============
if args.upload is not None:
    if(is_project()):
        _error = []
        print(args.upload[0])
        args.upload[0] = args.upload[0].replace('FileCabinet{slash}SuiteScripts{slash}'.format(slash=os.path.sep),'')
        print(args.upload[0])
        _path = os.path.join(CWD,'FileCabinet','SuiteScripts', args.upload[0])
        print(_path)
        _cmdsdfcli = None 
        with open(os.path.join(CWD,'.sdf'),'r+') as file:
            password = file.readlines()
            file.close()
        password = password[4].split('=')
        if os.path.isfile(_path):
            _cmdsdfcli = 'uploadfiles'
        elif os.path.isdir(_path):
            _cmdsdfcli = 'uploadfolders'
        
        if _cmdsdfcli is not None:
            proc = subprocess.Popen([SDFCLI,_cmdsdfcli,'-paths', '/SuiteScripts/{}'.format(args.upload[0]),'-p',CWD], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,shell = True)

            proc.stdin.write(password[1].encode())
            proc.stdin.flush()

            stdout, stderr = proc.communicate()
            _error = error_in_log()
            if len(_error) > 0:
                print("""{color}ERROR: No se ha podido realizar la carga{reset}""".format(color=fg('red'), reset=attr('reset')))                   
                for item in _error:
                    print("""{color}{error}{reset}""".format(color=fg('yellow'),error=item, reset=attr('reset')))
            else:
                print("""{color}Success: Se ha actualizado el archivo{reset}""".format(color=fg('cyan'), reset=attr('reset')))                   
        else:
            print("""{color}Error: El comando solo puede ejecutarse sobre archivos y rectorios regulares{reset}""".format(color=fg('yellow'), reset=attr('reset')))
    else:
        print("""{color}Error: El comando solo puede ejecutarse dentro de un proyecto{reset}""".format(color=fg('yellow'), reset=attr('reset'))) 
        exit()

#============== Deploy accountcustimization project ==============
if args.deploy:
    if(is_project()):
        subprocess.call([SDFCLI, 'deploy','-p', CWD], shell=True)
    else:
        print("""{color}Error: El comando solo puede ejecutarse dentro de un proyecto{reset}""".format(color=fg('yellow'), reset=attr('reset'))) 
        exit()
