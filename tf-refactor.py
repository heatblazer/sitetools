'''
THIS SCRIPT IS MADE FOR DEVELOPERS. 

terragrunt plan
switch to cache dir
tfswitch 0.13.7
terraform 0.13upgrade
terraform init -reconfigure
terraform state replace-provider "registry.terraform.io/-/aws" "hashicorp/aws"
tfswitch 0.14.11
terraform init
cd ../.../..
rm -rf .terragrunt-cache .terraform.lock.hcl
tfswitch --latest
terragrunt plan
(optional if errors like )
* Failed to execute "terraform init" in ./.terragrunt-cache/UwhbEZQ-CCxsVR-J1oLTzjzBNmA/WIV4UF7SiZWuR37AZa_KKhJYsAg
  ╷
  │ Error: Incompatible provider version
  │ 
  │ Provider registry.terraform.io/hashicorp/aws v3.23.0 does not have a
  │ package available for your current platform, darwin_arm64.
  │ 
  │ Provider releases are separate from Terraform CLI releases, so not all
  │ providers are available for all platforms. Other versions of this provider
  │ may have different platforms supported.
  ╵
  
  exit status 1
Do a slow crawl of TFM version updates until there are no errors by going down to the last module version that doesn't have these errors, e.g.
change module version
rm -rf .terragrunt-cache .terraform.lock.hcl
terragrunt plan
repeat until the latest TFM module version

'''

#verbosity
import warnings

#sys stuff
import os
import subprocess 
import sys
import socket
import datetime


####################
#user manual defines

GITREPO = ""



#################### UTILS
class Utils:
    """ Utulity functions - static class """


    class Cmd(object):
        """ spawn a new process and capture stdout and stderr"""
        def __init__(self, cmstr=None, verbose=False):
            self._cmstr = cmstr
            self._out = None
            self._err = None
            self._dataerr = []
            self.pro = None
            self._vmode = verbose

        def __call__(self):
            if self._cmstr is not None:
                self.execute(self._cmstr)

        def std_out(self):
            if self._out is not None:
                return self._out.decode('utf-8')
            else:
                return "None"

        def std_err(self):
            if self._err is not None:
                return self._err.decode('utf-8')
            else:
                return "None"

        def flush(self):
            self._out = None
            self._dataout = None
            self._err = None 

        def sys_exec(self, cmd):
            return os.system(cmd)

        def execute(self, cmd, term=True):
            cmd.strip()
            if self._vmode is True:
                term = True
            fp = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=term)
            self.pro = fp
            (self._out, self._err) = fp.communicate()
            return len(self._err) == 0

        def terminate(self):
            if self.pro is not None:
                self.pro.terminate()
            self.pro = None

        def kill(self):
            if self.pro is not None:
                self.pro.kill()
            self.pro = None
            

    sresult = [] 

    @staticmethod
    def unlink(fname):
        pass

    @staticmethod 
    def rmdir(dir_path):
        pass

    @staticmethod
    def getListOfFiles(dirName, opt=None):
        # create a list of file and sub directories 
        # names in the given directory 
        listOfFile = os.listdir(dirName)
        allFiles = list()
        for entry in listOfFile:            
            fullPath = os.path.join(dirName, entry)                
            # If entry is a directory then get the list of files in this directory 
            if os.path.isdir(fullPath):
                allFiles = allFiles + Utils.getListOfFiles(fullPath, opt)
            else:
                if opt is not None:
                    if opt(fullPath) is True:
                        allFiles.append(fullPath)
                else:
                    allFiles.append(fullPath)
        return allFiles

    @staticmethod
    def getDown(dirname, level=0):
        listOfFile = os.listdir(dirname)
        allFiles = list()
        for entry in listOfFile:            
            fullPath = os.path.join(dirname, entry)                
            # If entry is a directory then get the list of files in this directory 
            if level == 0:
                return allFiles
            if os.path.isdir(fullPath):
                allFiles.append(fullPath)
                allFiles = allFiles + Utils.getDown(fullPath, level-1)
        return allFiles

        pass

    @staticmethod
    def home_dir():
        return os.path.dirname(os.path.realpath(__file__))

    @staticmethod
    def home():
        #os.chdir(os.path.dirname(os.path.realpath(__file__)))
        return os.path.dirname(os.path.realpath(__file__))

    @staticmethod
    def mkdir(direntry):
        if Utils.dir_exists_ex(Utils.home() + "/" + direntry):
            return False
        os.mkdir(direntry)
        return True

    @staticmethod
    def chdir(newdir):
        root = str (newdir) 
        os.chdir(root)
        return root

    @staticmethod
    def dir_exists_ex(path, wdata=True):
        """wdata: mark False if only check for pathname, or default for path w contents"""
        res = False
        if os.path.isdir(path):
            if wdata is True:              
                res = len(os.listdir(path)) > 1
            res = True
        return res
    
    @staticmethod
    def find_file(dir, match):
        listOfFile = os.listdir(dir)
        allfiles = list()
        for entry in listOfFile:
            fullpath = os.path.join(dir, entry)
            if entry == match:
                Utils.sresult.append(fullpath)
            elif os.path.isdir(fullpath):
                allfiles = allfiles + Utils.find_file(fullpath, match)
            else:
                allfiles.append(fullpath)
        return allfiles

    @staticmethod
    def quick_cmp(str1, str2, exact=False):
        l1 = len(str1)
        l2 = len(str2)
        if exact and l1 != l2:
            return False 
        strlen = l2 if l1 > l2 else l1
        i=0
        for i in range(0, strlen):
            if str1[i] != str2[i]:
                break
        return str1[i] > str2[i]
        
    @staticmethod
    def btoi(bdat, endiness=False):
        integerpart = []
        for b in bdat:
            integerpart.append(int(b))
        if endiness is False:
            integerpart.reverse()
        result = 0
        for i in range(0, len(integerpart)):
            result |= integerpart[i] << (i * 8)                    
        return result 

#################  UTILS


class InitializeAll:

    def __init__(self, rootfolder):
        r = "{}".format(rootfolder)
        print(r)
        self.rootfolder = Utils.chdir(r)
        self.planned = []
        files = Utils.getListOfFiles(self.rootfolder, lambda p: True if "terragrunt.hcl" in p and "terragrunt-cache" not in p else False)
        for f in files:
            f = f.split("/")
            f = "/{}".format("/".join(f[1:-1]))    
            self.planned.append(f)
        pass

    
    def tfSwitchFix(self, fix=False):
        for p in self.planned:
            print(p)
        
        for p in self.planned:
            Utils.chdir(p)
            cached = Utils.getDown(p, 3)
            for c in cached:
                print(c)
                tfexe = "{}/run/macos/tfswitch".format(Utils.home_dir())
                shell = Utils.Cmd()
                Utils.chdir(cached[-1])
                if fix is True:
                    shell.sys_exec("{} 0.13.7".format(tfexe))
                    shell.sys_exec("terraform 0.13 upgrade")
                    shell.sys_exec("terraform init -reconfigure")
                    shell.sys_exec('terraform state replace-provider "registry.terraform.io/-/aws" "hashicorp/aws"')
                    shell.sys_exec("{} 0.14.11".format(tfexe))
                    shell.sys_exec('terraform init')
                    Utils.chdir(p) # root folder
                    shell.sys_exec("rm -rf .terragrunt-cache .terraform.lock.hcl")
                    shell.sys_exec("{} --latest".format(tfexe))
                    shell.sys_exec("terragrunt plan")

    def validateAll(self):
        v = Utils.Cmd()
        for p in self.planned:
            Utils.chdir(p)
            print("Start validating on {}".format(p))
            v.execute("terragrunt validate")
            print(v.std_err())

    def planAll(self, omit=False):
        if omit is False:
            for p in self.planned:
                print(p)
            return 
        for p in self.planned:
            shell = Utils.Cmd()
            Utils.chdir(p)
            print("change to {}".format(p))
            shell.execute("terragrunt plan")
            if "ERROR" in shell.std_err():
                print("ERROR")
                print(shell.std_err())


if __name__ == "__main__":
    if True:
        ref = InitializeAll("/Users/izapryanov/Desktop/todo/tg-infra-sheetlog/live/prod/ap-southeast-2/prod")
        ref.validateAll()
#        ref.planAll()
#        ref.tfSwitchFix()
    else:
        if len(sys.argv) < 2:
            print("error: provide path to repo")
            exit(-1)
        
        plan = False
        if sys.argv[2] is not None and sys.argv[2] == "-p":
            plan = True

        print("Starting up itf-refactor: {}".format(sys.argv[1]))
        ref = InitializeAll(sys.argv[1])
        ref.planAll(plan)
        ref.tfSwitchFix()
        pass

    