import os
import sys
import random
import networkx as nx
import xml.etree.ElementTree as ET
import re

install_prefix = os.path.join( os.getcwd(), "../scripts/")
sys.path.append(install_prefix)
import interface
################################################################
################################################################

canvas = None
# 必须包含一个init函数，该函数在初始化时被调用一次，用于创建自定义内容
def init():
    global canvas
    canvas = interface.getComponentByCid(66)
    

# 必须包含一个tick函数，这个函数将在每一帧被调用，dt为距离上一次调用经过的时间（毫秒）
def tick(dt):
    global canvas
    canvas.update()

################################################################
################################################################

packages_found  = []
package_include_content = {}
package_include_directories   = {}
package_target_link_libraries = {}
package_cmakelist_path        = {}
package_depend_content        = {}

def read_add_executable_in_cmakelists(path):
    # 读取"CMakeLists.txt"文件
    with open(path, 'r') as f:
        cmakelists = f.read()

    # 找出所有.c/.cpp文件
    source_files = re.findall(r'add_executable\((.*?)\)', cmakelists, re.DOTALL)
    source_files = [file.strip() for sublist in source_files for file in sublist.split()]
    source_files = [file for file in source_files if file.endswith('.cpp') or file.endswith('.c')]
    return source_files


def unpack_variable(cmakelists_content, components_list):
    unpacked_components_list = []
    variables                = []
    pattern                  = re.compile(r'\$\{(.*?)\}')
    for component in components_list:
        m = pattern.match(component)
        if m:
            variables.append(m.group(1))
        else:
            unpacked_components_list.append(component)
    
    for variable in variables:
        pattern = re.compile(r'set\(\s*'+ re.escape(variable) + r'\s*(.*?)\)', re.DOTALL)
        m = pattern.search(cmakelists_content)
        if m:
            variable_value = m.group(1).strip().split()
            variable_value = unpack_variable(cmakelists_content , variable_value) # 递归变量解包
            unpacked_components_list.extend(variable_value)
        else:
            ori_var = "${" + variable + "}"
            variable_value.append(ori_var)
    
    return unpacked_components_list



def read_find_package_in_cmakelists(path):
    # 读取"CMakeLists.txt"文件
    with open(path, 'r') as f:
        cmakelists = f.read()

    # 将 cmakelists 分割成行
    lines = cmakelists.splitlines()
    # 过滤掉所有以 "#" 开头的行
    filtered_lines = [line for line in lines if not line.strip().startswith("#")]
    # 将过滤后的行重新组合成一个字符串
    cmakelists = "\n".join(filtered_lines)
    
    # 找出所有find_package中试图搜索的包的名字
    package_names = re.findall(r'find_package\((.*?)\)', cmakelists, re.DOTALL)
    # 将找到的包的名字进行处理，去除多余的空格和换行符
    idi_names = [item for name in package_names for item in name.strip().split()]

    for block in package_names:
        components = re.search(r'REQUIRED COMPONENTS(.*)', block, re.DOTALL)
        if components:
            # 将找到的内容分割成行，并移除前后的空白字符
            lines = [line.strip() for line in components.group(1).splitlines() if line.strip()]
            # 再以空格分割
            components_list = [component for line in lines for component in line.split() if component]
            components_list = unpack_variable( cmakelists, components_list)
            idi_names.extend(components_list)

    return idi_names


def read_include_directories_in_cmakelists(path):
    # 读取"CMakeLists.txt"文件
    with open(path, 'r') as f:
        cmakelists = f.read()

    # 将 cmakelists 分割成行
    lines = cmakelists.splitlines()
    # 过滤掉所有以 "#" 开头的行
    filtered_lines = [line for line in lines if not line.strip().startswith("#")]
    # 将过滤后的行重新组合成一个字符串
    cmakelists = "\n".join(filtered_lines)
    
    include_directories_names = re.findall(r'\binclude_directories\((.*?)\)', cmakelists, re.DOTALL)
    # 将找到的包的名字进行处理，去除多余的空格和换行符
    include_directories_names = [item for name in include_directories_names for item in name.strip().split()]

    return include_directories_names

def read_depends_in_package_xml(root):
    run_depends   = [elem.text for elem in root.iter('run_depend')]
    build_depends = [elem.text for elem in root.iter('build_depend')]

    run_set   = set(run_depends)
    build_set = set(build_depends)

    # 找到共有的部分
    common = run_set & build_set
    common_list = list(common)
    return common_list


fake_packages = ['EXACT', 'COMPONENTS', 'REQUIRED', 'QUIET', 'NO_MODULE']
def is_fake_package(p):
    if p in fake_packages:
        return True
    pattern = re.compile(r'\d+\.\d+')
    if pattern.match(p):
        return True
    return False
    
def find_packages_and_set_G(path , G):
    global packages_found, package_include_content, package_include_directories, package_target_link_libraries, package_depend_content,package_cmakelist_path
    # 遍历目录
    for root_dir, dirs, files in os.walk(path):
        # 检查是否包含"package.xml"文件
        if "package.xml" in files:
            # 解析"package.xml"文件
            tree = ET.parse(os.path.join(root_dir, "package.xml"))
            root = tree.getroot()
            # 读取功能包的名称
            package_name = root.find('name').text
            packages_found.append(package_name)
            G.add_node(package_name)

            #更新包的depend内容
            depends_packages = read_depends_in_package_xml(root)
            package_depend_content[package_name] = depends_packages

            # 检查是否包含"CMakeLists.txt"文件
            if "CMakeLists.txt" in files:
                cmakelist_file_path = os.path.join(root_dir, "CMakeLists.txt")

                # 添加到字典
                package_cmakelist_path[package_name] = cmakelist_file_path

                # 读取"CMakeLists.txt"文件
                dep_package_names = read_find_package_in_cmakelists( cmakelist_file_path )
                for dep_pn in dep_package_names:
                    if is_fake_package(str(dep_pn)):
                        continue
                    G.add_edge(dep_pn, package_name)

                # 寻找全局include_directories:
                package_include_directories[package_name] = read_include_directories_in_cmakelists(cmakelist_file_path)

                # 下面是找CPP并从中寻找include内容的部分
                source_files = read_add_executable_in_cmakelists(cmakelist_file_path)
                # 遍历每个.c/.cpp文件
                for source_file in source_files:
                    # 检查文件是否存在
                    if os.path.exists(os.path.join(root_dir, source_file)):
                        # 读取文件
                        with open(os.path.join(root_dir, source_file), 'r') as f:
                            source_code = f.read()

                        #找出所有引用的头文件
                        include_files = re.findall(r'#include\s*[<"]([^>"]*)[>"]', source_code)

                        #打印出功能包的名称和引用的头文件
                        include_str = ""
                        for include_file in include_files:
                            include_str += include_file
                            include_str += '\n'
                        package_include_content[package_name] = include_str
                        

# 在下面添加自定义回调函数
def scan_cmake_callback():
    global packages_found, canvas, package_include_content, package_include_directories, package_target_link_libraries, package_depend_content, package_cmakelist_path
    print("Scan:")
    packages_found  = []
    package_include_content = {}
    package_include_directories   = {}
    package_target_link_libraries = {}
    package_depend_content        = {}
    package_cmakelist_path        = {}

    G = nx.DiGraph()

    abs_dir     = os.path.dirname(os.path.abspath(__file__))
    normed_path = os.path.normpath(os.path.join(abs_dir, "../../src"))
    print(normed_path)
    interface.getComponentByCid(22).feedString("Scanning: " + normed_path + "\n")
    find_packages_and_set_G(normed_path , G)
    canvas.setG(G, packages_found)
    canvas.setIncludeContent(package_include_content)
    canvas.setIncludeDirectories(package_include_directories)
    canvas.setIncludeDependContent(package_depend_content)
    canvas.setCmakeListPathes(package_cmakelist_path)
    interface.getComponentByCid(22).feedString("> Scan finish.\n")
    

   

def button2_callback():
    interface.getComponentByCid(22).feedString("中文尝试")


def scale_callback( value ):
    global canvas
    canvas.setScale(value)

def custom_callback():
    global canvas
    canvas.setShow(1)

def all_callback():
    global canvas
    canvas.setShow(2)

def include_g_callback():
    global canvas
    canvas.setShow(3)

def layer_callback(state):
    global canvas
    canvas.setLayerLayout(state)
