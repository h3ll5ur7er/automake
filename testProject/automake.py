import subprocess as sp
import os
import re
from pprint import pprint

GCC_PATH = "C:/mingw/i686-8.1.0-posix-dwarf-rt_v6-rev0/mingw32/bin/gcc.exe"
GPP_PATH = "C:/mingw/i686-8.1.0-posix-dwarf-rt_v6-rev0/mingw32/bin/g++.exe"

CFLAGS = [
    "-Wall",
    "-fmessage-length=0"
]

CPPFLAGS = [
    "-fno-exceptions",
    "-std=c++11"
] + CFLAGS

LIBRARIES = []
WINDOWS_LDFLAGS = []

OPTIMIZE = "-g3"

_LIBS = [f"-l{l}" for l in LIBRARIES]
LDFLAGS = [
    OPTIMIZE,
    "-Lobj",
    *_LIBS,
    *WINDOWS_LDFLAGS,
    "-static",
    "-static-libgcc",
    "-static-libstdc++"
]

class FileFinder:
    def __init__(self, regex_pattern, flags=0):
        self._matcher = re.compile(regex_pattern, flags)

    def find(self, root="."):
        matching_files = []        
        for base_path, _, files in os.walk(root):
            for file_name in files:
                full_path = os.path.join(base_path, file_name)
                if self._matcher.match(full_path):
                    matching_files.append(full_path)
        return matching_files

class CFileFinder(FileFinder):
    def __init__(self):
        super().__init__(r".*\.c$")

class HFileFinder(FileFinder):
    def __init__(self):
        super().__init__(r".*\.h$")

class CppFileFinder(FileFinder):
    def __init__(self):
        super().__init__(r".*\.cpp$")

class HppFileFinder(FileFinder):
    def __init__(self):
        super().__init__(r".*\.hpp$")

class OFileFinder(FileFinder):
    def __init__(self):
        super().__init__(r".*\.o$")

def run(cmd):
    return  sp.check_output(cmd, stderr=sp.STDOUT)

def compile_c(path):
    h_file_finder = HFileFinder()
    h_files = h_file_finder.find(path)
    
    h_file_dirs = list(set(map(lambda p: os.path.dirname(p), h_files)))

    c_file_finder = CFileFinder()
    c_files = c_file_finder.find(path)
    print("--- compiling c files: ---")
    for c_file in c_files:
        obj_file = c_file.replace("/src/", "/obj/").replace(".c", ".o")
        print(run([GCC_PATH, "-c", *CFLAGS, *[f"-I{p}" for p in h_file_dirs], c_file, "-o", obj_file]))
    
def compile_cpp(path):
    hpp_file_finder = HppFileFinder()
    hpp_files = hpp_file_finder.find(path)
    
    hpp_file_dirs = list(set(map(lambda p: os.path.dirname(p), hpp_files)))

    cpp_file_finder = CppFileFinder()
    cpp_files = cpp_file_finder.find(path)

    print("--- compiling cpp files: ---")
    for cpp_file in cpp_files:
        obj_file = cpp_file.replace("/src/", "/obj/").replace(".cpp", ".o")
        print(run([GPP_PATH, "-c", *CPPFLAGS, *[f"-I{p}" for p in hpp_file_dirs], cpp_file, "-o", obj_file]))
    
def compile(path):
    compile_c(path)
    compile_cpp(path)

def link(path, name):
    print("--- linking: ---")
    obj_file_finder = OFileFinder()
    obj_files = obj_file_finder.find(path)
    print(run([GCC_PATH, *obj_files, *LDFLAGS, "-o", name]))

def build(path, name):
    compile(path)
    link(path, name)

if __name__ == "__main__":
    from sys import argv
    if len(argv) != 3:
        print("usage: python automake.py <root_path> <executable_name>")
    else:
        build(argv[1], argv[2])
