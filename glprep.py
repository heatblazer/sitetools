'''
THIS SCRIPT IS MADE FOR DEVELOPERS. 
If you are just looking for a devops or dev sec ops or whatever ops you are and have no idea what Vulka, Glfw and GLM are and how to build them separately,
don't bother with this.
GLFW and Vulkan have a lot of prerequisites, please prepare those before you run the script. The script does not deal with apt install or dnf install
for xrandr-devel or mesa drivers.
This is a simple and stupid script to setup vulkan with glfw and glm for development. A lot of tutorials and guides were present on the net
however all of them is missing the `push one button and wait`. This script as is not perfect aims to achieve this.
The below variables GLM GLFW and VULKAN can and shall (Vulkan especially) be changed with the relevant links. 
This thing is supposed to be run as a one command. 
It will - clone glfw glm and download vulkan. 
It will - create a folder External and put all of the needed include and lib for all of those.
It will create a one folder to put in your root and just use it in your projects.
It will create a hint cmake file what to include and how to link (yeah since there are always tons of questions how to do that)
It will NOT install any prerequisites.
It will not ask you for a password besides the ./vulkansk script that builds vulkan  bash.sys_exec("./vulkansdk --maxjobs --skip-deps") if you are not happy
with that remove the line and run it later.

I am not a pro when doing those yak shaving 1000 times so I've made it for other that want to focus on the graphics instead of the artrocious setups we
have to deal each time.

Have fun.
'''

#verbosity
import warnings

#sys stuff
import os
import subprocess 
import sys
import socket
import datetime
import requests
#User modified
GLM = "git clone https://github.com/g-truc/glm"
GLFW = "git clone https://github.com/glfw/glfw"
VULKAN = "https://sdk.lunarg.com/sdk/download/1.3.275.0/linux/vulkansdk-linux-x86_64-1.3.275.0.tar.xz"



#################### UTILS
class Utils:
    """ Utulity functions - static class """

    class Cmd(object):
        """ spawn a new process and capture stdout and stderr"""

        def __init__(self, cmstr=None, verbose=False):
            self._cmstr = cmstr
            self._out = None
            self._err = None
            self._dataout = []
            self._dataerr = []
            self.pro = None
            self._vmode = verbose


        def __call__(self):
            if self._cmstr is not None:
                self.execute(self._cmstr)


        def std_out(self):
            if self._out is not None:
                return self._out
            else:
                return None


        def std_out_data(self):
            return self._dataout


        def std_err(self):
            if self._err is not None:
                return self._err
            else:
                return None


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


        def execute_ex(self, cmd):
            cmd.strip()
            fp = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            while True:
                line = fp.stdout.readline()
                if not line:
                    break
                else:
                    self._dataout.append(line)                        

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
                if opt is not None and opt(fullPath) is False:
                    allFiles.append(fullPath)
                elif opt is None:
                    allFiles.append(fullPath)
        return allFiles


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
    def quick_cmp(str1, str2):
        l1 = len(str1)
        l2 = len(str2)
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

    def __init__(self):
        self.vkpath = None
        pass

    def find_vk_dir(self):
        for d in os.listdir("{}/tmp".format(Utils.home())):
            if os.path.isdir(d):
                self.vkpath = "{}/tmp/{}".format(Utils.home(), d)

    def prep_vulkan(self):
        print ("Enter preparing VULKAN, may take a while...")
        try:
            r = requests.get(VULKAN, allow_redirects=True)
            open('vktmp.tar.xz', 'wb').write(r.content)
            tar = Utils.Cmd("tar -xf *")
            tar()
            tar = Utils.Cmd("rm vktmp.tar.xz")
            tar()
            self.find_vk_dir()
            Utils.chdir(self.vkpath)
            print(self.vkpath)
            bash = Utils.Cmd()
            bash.sys_exec("./vulkansdk --maxjobs --skip-deps")
            bash.sys_exec("source setup-env.sh")
            bash.sys_exec("cp -rf {}/* {}/External/vulkan".format(self.vkpath, Utils.home()))
        except:
            print("Invalid file or URL")



    def prep_glm(self):
        print ("Enter preparing GLM")
        git = Utils.Cmd(GLM)
        git()
        Utils.chdir("{}/tmp/glm".format(Utils.home()))
        git = Utils.Cmd("cp -r glm/ {}/External/include".format(Utils.home()))
        git()
        print("Finished preparing GLM")


    def prep_glfw(self):
        print("Enter preparing GLFW")
        git = Utils.Cmd(GLFW)
        git()
        Utils.chdir("{}/tmp/glfw".format(Utils.home()))
        git = Utils.Cmd("cp -r include/ {}/External".format(Utils.home()))
        git()
        git.execute("cmake -S . -B build")
        print(git.std_out())
        Utils.chdir("{}/tmp/glfw/build".format(Utils.home()))
        git.execute("make")
        print(git.std_out())
        Utils.chdir("{}/tmp/glfw/build/src".format(Utils.home()))
        git = Utils.Cmd("cp *.a {}".format(Utils.home_dir()+"/"+"External/lib"))
        git()
        print("Finished preparing GLFW")


    def init_all(self):
        Utils.home()
        Utils.mkdir("tmp")
        Utils.mkdir("External")
        Utils.chdir(Utils.home() + "/" + "External")
        Utils.mkdir("lib")
        Utils.mkdir("lib64")
        Utils.mkdir("include")
        Utils.mkdir("vulkan")
        Utils.chdir(Utils.home() + "/" + "tmp")
        self.prep_vulkan()
        Utils.chdir(Utils.home() + "/" + "tmp")
        self.prep_glfw()
        Utils.chdir(Utils.home() + "/" + "tmp")
        self.prep_glm()
        deleter = Utils.Cmd("rm -rf * {}/tmp".format(Utils.home()))
        deleter()

    def create_cmake(self):
        print("Creating CMAKE helper directives")
        Utils.chdir("{}/External".format(Utils.home()))
        try:
            fp = open("cmake_directives.txt", "w+")
            fp.write('# please replace `replace-me` with the executable or binary you are linikg the project to\n')
            fp.write('# please put the External folder to the CMAKE_SOURCE_DIR (root of your project)\n')
            fp.write('# copy paste the below CMAke directives to your project\n')
            fp.write('find_package(Vulkan REQUIRED FATAL_ERROR)\n')
            fp.write('target_include_directories(replace-me PRIVATE ${CMAKE_SOURCE_DIR}/External/include ${CMAKE_SOURCE_DIR}/External/vulkan/include) \n')
            fp.write('add_library(libglfw3 STATIC IMPORTED)\n')
            fp.write('link_directories(${CMAKE_SOURCE_DIR}/External/lib)\n')
            fp.write('link_directories(${CMAKE_SOURCE_DIR}/External/lib64)\n')
            fp.write('target_link_libraries(replace-me glfw3)\n')
            fp.write('target_link_libraries(replace-me vulkan)\n')            
            fp.close()
        except:
            pass


if __name__ == "__main__":
    print("Starting up preparation...")
    initializer = InitializeAll()
    initializer.init_all()
    #initializer.create_cmake()

    