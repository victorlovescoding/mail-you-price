from flask import Flask,session,redirect
from flask import request
from flask import render_template
import pymongo,certifi,json
#APScheduler 
from apscheduler.schedulers.background import BackgroundScheduler

#資料庫連接
client = pymongo.MongoClient("xxx", tlsCAFile=certifi.where())
db = client.test #操作資料庫
collection=db.users #操作users集合
app=Flask(
    __name__,
    static_folder="public",
    static_url_path="/"    
)

app.secret_key="any string but secret"

@app.route('/')
def index():
    #進到首頁時，如果原本已經登入，就直接進入會員系統
    if 'mail' in session:
        mail=session.get('mail')
        return render_template('member.html',mail=mail)
        
    else:
        return render_template('index.html')
    

@app.route('/',methods=["POST"])
def signUp():
    name = request.form["name"]
    mail = request.form["mail"]
    password = request.form["password"]

    result=collection.find_one({
        "$and":[
            {"name":name},
            {"mail":mail}
        ]
    })
    if result==None:
        collection.insert_one({
            "name":name,
            "password":password,
            "mail":mail,
            "productData":[]
        })
        return render_template('index.html', successMsg="註冊成功!")
    else:
        return render_template('index.html', successMsg="該信箱已被註冊")
    


        

@app.route('/member',methods=["POST"])
def logIn():
    mail = request.form["mail"]
    password = request.form["password"]
    result=collection.find_one({
    "$and":[
        {"mail":mail},
        {"password":password}
        ]
    })
    if result==None:
        return render_template('index.html', successMsg="帳號或密碼輸入錯誤")
    else:
        session['mail']=mail
        #回報前端使用者資料有幾筆
        # sendDataLength(mail)
        #登入時，找出mongoDB裡的productName，並傳送給使用者
        userData=collection.find_one({
        "mail":mail
    })
        productData=userData["productData"]
        name=userData["name"]
        dataLength=len(productData)
        allProduct=[]
        if productData==[]:
            return render_template('member.html',mail=mail)
        else:
            for num in range(dataLength):
                if productData[num]["productName"]!="":
                    allProduct.append(productData[num])
            productData=str(productData)
            return render_template('member.html',productData=allProduct,name=name)

@app.route('/logout')
def logOut():
    if 'mail' in session:
        del session['mail']
        return render_template('index.html')
    else:
        return render_template('index.html')
#如果沒有session貼會員系統網址不給進
@app.route('/member.html')
def memberHTML():
    if 'mail' in session:
        mail=session.get('mail')
        userData=collection.find_one({
        "mail":mail
        })
        productData=userData['productData']
        name=userData['name']
        allProduct=[]
        dataLength=len(productData)
        for num in range(dataLength):
            if productData[num]["productName"]!="":
                allProduct.append(productData[num])
        return render_template('member.html',productData=allProduct,name=name)
    else:

        return render_template("index.html")
#沒有session貼會員系統網址不給進
@app.route('/member') 
def member():
    if 'mail' in session:
        mail=session.get('mail')

        userData=collection.find_one({
        "mail":mail
    })
        productData=userData["productData"]
        name=userData["name"]
        dataLength=len(productData)
        allProduct=[]
        if productData==[]:
            return render_template('member.html',name=name)
        else:
            for num in range(dataLength):
                if productData[num]["productName"]!="":
                    allProduct.append(productData[num])      
            return render_template('member.html',dataLength=dataLength,productData=allProduct,name=name)
    else:
        return redirect("/")
    


@app.route('/member.html',methods=['POST']) #動態路由
def getPrice():  
    import urllib.request as req
    site=request.form["productSite"]
    originSite=request.form["productSite"]
    if site[8:11]=="24h":
        mail=session.get('mail')
        #判斷網址是否有"?"
        if site.find("?")==-1:       
            # commodity="https://24h.pchome.com.tw/prod/QAAF7N-A9006CPTZ"
            site=site.replace("https://24h.pchome.com.tw/prod/","")
            # url="https://ecapi.pchome.com.tw/ecshop/prodapi/v2/prod/button&id=&fields=Seq,Id,Price,Qty,ButtonType,SaleStatus,isPrimeOnly,SpecialQty,Device&_callback=jsonp_prodbutton&1662133140?_callback=jsonp_prodbutton"
            url="https://ecapi.pchome.com.tw/ecshop/prodapi/v2/prod/"+site[0:16]+"&fields=Seq,Id,Name,Nick,Store,PreOrdDate,SpeOrdDate,Price,Discount,Pic,Weight,ISBN,Qty,Bonus,isBig,isSpec,isCombine,isDiy,isRecyclable,isCarrier,isMedical,isBigCart,isSnapUp,isDescAndIntroSync,isFoodContents,isHuge,isEnergySubsidy,isPrimeOnly,isPreOrder24h,isWarranty,isLegalStore,isFresh,isBidding,isSet,Volume,isArrival24h,isETicket,ShipType,isO2O,RealWH,ShipDay,ShipTag,isEbook,isSubscription,Subscription&_callback=jsonp_prodmain&1662364260?_callback=jsonp_prodmain"
            with req.urlopen(url) as response:
                commodity=response.read().decode("utf-8")
            import json
            commodity=commodity.replace('try{jsonp_prodmain(','')
            commodity=commodity.replace(');}catch(e){if(window.console){console.log(e);}}','')
            commodity=json.loads(commodity)
            productName=str(commodity[site+"-000"]["Name"])
            collection.update_one({
                "mail":mail
            },{
                "$push":{
                    "productData":
                        {"productName":productName,"productSite":originSite}
                }
            })

            #更新使用者資料庫後，馬上回傳使用者所有追蹤的網站(包含剛剛新增的)
            userData=collection.find_one({
            "mail":mail
            })
            productData=userData["productData"]
            name=userData["name"]
            dataLength=len(productData)
            allProduct=[]
            for num in range(dataLength):
                if productData[num]["productName"]!="":
                    allProduct.append(productData[num])
            return render_template('member.html',dataLength=dataLength,productData=allProduct,name=name)

        else:
            #若確定網址有"?"就將?以及後面網址刪除，以利得到產品編號
            lengthOfSite=len(site)
            startOfDelete=site.find("?")
            noNeedSite=site[startOfDelete:lengthOfSite]
            needSite=site.replace(noNeedSite,'')
            # commodity="https://24h.pchome.com.tw/prod/QAAF7N-A9006CPTZ"
            site=needSite.replace("https://24h.pchome.com.tw/prod/","")
            # url="https://ecapi.pchome.com.tw/ecshop/prodapi/v2/prod/button&id=&fields=Seq,Id,Price,Qty,ButtonType,SaleStatus,isPrimeOnly,SpecialQty,Device&_callback=jsonp_prodbutton&1662133140?_callback=jsonp_prodbutton"
            url="https://ecapi.pchome.com.tw/ecshop/prodapi/v2/prod/"+site[0:16]+"&fields=Seq,Id,Name,Nick,Store,PreOrdDate,SpeOrdDate,Price,Discount,Pic,Weight,ISBN,Qty,Bonus,isBig,isSpec,isCombine,isDiy,isRecyclable,isCarrier,isMedical,isBigCart,isSnapUp,isDescAndIntroSync,isFoodContents,isHuge,isEnergySubsidy,isPrimeOnly,isPreOrder24h,isWarranty,isLegalStore,isFresh,isBidding,isSet,Volume,isArrival24h,isETicket,ShipType,isO2O,RealWH,ShipDay,ShipTag,isEbook,isSubscription,Subscription&_callback=jsonp_prodmain&1662364260?_callback=jsonp_prodmain"
            with req.urlopen(url) as response:
                commodity=response.read().decode("utf-8")
            import json
            commodity=commodity.replace('try{jsonp_prodmain(','')
            commodity=commodity.replace(');}catch(e){if(window.console){console.log(e);}}','')
            commodity=json.loads(commodity)
            productName=str(commodity[site+"-000"]["Name"])
            collection.update_one({
                "mail":mail
            },{
                "$push":{
                    "productData":
                        {"productName":productName,"productSite":needSite}
                }
            })

            #更新使用者資料庫後，馬上回傳使用者所有追蹤的網站(包含剛剛新增的)
            userData=collection.find_one({
            "mail":mail
            })
            productData=userData["productData"]
            name=userData["name"]
            dataLength=len(productData)
            allProduct=[]
            for num in range(dataLength):
                if productData[num]["productName"]!="":
                    allProduct.append(productData[num])
            return render_template('member.html',dataLength=dataLength,productData=allProduct,name=name)

    else:
        mail=session.get('mail')
        userData=collection.find_one({
        "mail":mail
        })
        productData=userData["productData"]
        name=userData["name"]
        dataLength=len(productData)
        allProduct=[]
        for num in range(dataLength):
            if productData[num]["productName"]!="":
                allProduct.append(productData[num])
        return render_template('member.html',dataLength=dataLength,productData=allProduct,name=name,error="抱歉!該網址不支援，請換其他商品")
#刪除section
@app.route('/delete.html',methods=["POST"])
def delete():
    if 'mail' in session:
        deleteItem=request.form["deleteItem"]
        deleteItem=deleteItem.replace("購物去","")
        deleteItem=deleteItem.rstrip(" ")
        deleteItem=deleteItem.lstrip(" ")
        mail=session.get('mail')
        userData=collection.find_one({
        "mail":mail
        })
        productData=userData["productData"]
        name=userData["name"]
        dataLength=len(productData)
        
        #刪除使用者要刪除的商品
        for num in range (dataLength): 
            if productData[num]["productName"]==deleteItem:
                collection.update_one({
                "mail":mail
                },{
                    "$set":{
                        f"productData.{num}.productName":"",
                        f"productData.{num}.productSite":""
                        
                    }
                })
              
        #
        if productData==[]:
            return render_template('member.html',mail=mail)
        else:
            allProduct=[]
            dataLength=len(productData)
            userData=collection.find_one({
            "mail":mail
            })
            productData=userData["productData"]
            name=userData["name"]
            for num in range(dataLength):
                if productData[num]["productName"]!="":
                    allProduct.append(productData[num])      
            return render_template('member.html',productData=allProduct,name=name)
    else:
        return redirect("/")

@app.route('/delete.html')
def deleteHtml():
    if 'mail' in session:
        mail=session.get('mail')
        userData=collection.find_one({
        "mail":mail
    })
        productData=userData["productData"]
        name=userData["name"]
        dataLength=len(productData)
        allProduct=[]
        if productData==[]:
            return render_template('member.html',mail=mail)
        else:
            for num in range(dataLength):
                if productData[num]["productName"]!="":
                    allProduct.append(productData[num])      
            return render_template('member.html',dataLength=dataLength,productData=allProduct,name=name)
    else:
        return redirect("/") 

#自動化部分
def sendDataLength(mail):
    data=collection.find_one({
    "mail":mail
    })
    data=data["productData"]
    dataLength=len(data)
    return render_template('member.html',dataLength=dataLength)

   

def crawlerPrice(site,mail,name,productName):  
    import urllib.request as req
    if site[8:11]=="24h":
        # commodity="https://24h.pchome.com.tw/prod/QAAF7N-A9006CPTZ"
        newSite=site.replace("https://24h.pchome.com.tw/prod/","")
        # url="https://ecapi.pchome.com.tw/ecshop/prodapi/v2/prod/button&id=&fields=Seq,Id,Price,Qty,ButtonType,SaleStatus,isPrimeOnly,SpecialQty,Device&_callback=jsonp_prodbutton&1662133140?_callback=jsonp_prodbutton"
        url="https://ecapi.pchome.com.tw/ecshop/prodapi/v2/prod/"+newSite[0:16]+"&fields=Seq,Id,Name,Nick,Store,PreOrdDate,SpeOrdDate,Price,Discount,Pic,Weight,ISBN,Qty,Bonus,isBig,isSpec,isCombine,isDiy,isRecyclable,isCarrier,isMedical,isBigCart,isSnapUp,isDescAndIntroSync,isFoodContents,isHuge,isEnergySubsidy,isPrimeOnly,isPreOrder24h,isWarranty,isLegalStore,isFresh,isBidding,isSet,Volume,isArrival24h,isETicket,ShipType,isO2O,RealWH,ShipDay,ShipTag,isEbook,isSubscription,Subscription&_callback=jsonp_prodmain&1662364260?_callback=jsonp_prodmain"
        with req.urlopen(url) as response:
            commodity=response.read().decode("utf-8")
            #如果沒有出現下面的訊息代表該商品還在架上
            if commodity!="try{jsonp_prodmain([]);}catch(e){if(window.console){console.log(e);}}":
                import json
                commodity=commodity.replace('try{jsonp_prodmain(','')
                commodity=commodity.replace(');}catch(e){if(window.console){console.log(e);}}','')
                commodity=json.loads(commodity)
                productName=str(commodity[newSite+"-000"]["Name"])
                price=str(commodity[newSite+"-000"]["Price"]["P"])
                pic=str(commodity[newSite+"-000"]["Pic"]["B"])
                priceMin=""
                priceMax=""
                return sendMail(priceMin,priceMax,productName,price,mail,site,pic,name)
            else:
                #商品沒在架上，發信通知使用者
                return sendNoProductMail(productName,mail,name)


def getSiteFromDb():
    db = client.test #操作資料庫
    collection=db.users #操作users集合
    cursor=collection.find()
    for getSiteandMail in cursor:
        productData=getSiteandMail["productData"]
        mail=getSiteandMail['mail']
        name=getSiteandMail['name']
        if productData!=[]:
            for num in range(len(getSiteandMail["productData"])):
                site=getSiteandMail["productData"][num]["productSite"]
                productName=getSiteandMail["productData"][num]["productName"]
                crawlerPrice(site,mail,name,productName)
        else:
            return
            

def sendNoProductMail(productName,mail,name):
    #sendMail(productName,mail,name)
    import email.message
    msg=email.message.EmailMessage()
    msg["From"]="mrcrawler987@gmail.com"
    msg["To"]=mail
    msg["Subject"]="商品下架通知:"+productName
    #HTML內容
    msg.add_alternative("""\
        <head>
    <meta charset="UTF-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Document</title>
    </head>
    <body style="background-color: #F5F6F7;
            box-sizing: border-box;">
    <div class="content" 
        style="background: linear-gradient(130deg, #A4BFEF 50%, #6A93CB 100%);
                width:70vw;
                margin:auto;
                ">
        <p style="margin: 1rem;
                padding: 1rem;
                font-weight: 500;
                font-size: 1.3rem;
                color:#000000">Hi　"""+name+""":</p>
        <h2 style="text-align: center;color:#000000">"""+productName+"""</h2>
        <h3 style="text-align: center; color:red">很抱歉! 您所追蹤的商品已下架。</h3>
        <img src="https://cdn.pixabay.com/photo/2018/01/04/15/51/404-error-3060993__340.png" alt="" 
        style="display: block;width: 35%;
               margin: auto; padding: 1rem;
               border-radius: 20px;
               object-fit:cover">
        <a href='https://nf8wc6rczr.ap-northeast-1.awsapprunner.com/' style="display: block;
        text-align: center;
        font-size: 1.3rem;
        color:#000000;
        width: fit-content;
        margin: auto;
        background-color: #353b48;
        color: #FFFFFF;
        text-decoration: none;
        padding: .5rem 2rem;
        border-radius: 30px;">新增其他商品</a><br>
    </div>
        <footer style="background-color: #e3e3e3;
                        width: 70vw;
                        margin: auto;
                        padding: 2rem 0;">
            <p style="margin-left: 1rem;
                    color: #888888;
                    text-align: center;">©Copyright 2022 by Mr.crawler987 Taiwan</p>
        </footer>
    </body>
    </html>
            """,subtype="html")
    import smtplib
    server=smtplib.SMTP_SSL("smtp.gmail.com",465)
    server.login("mrcrawler987@gmail.com","xxx")
    server.send_message(msg)
    server.close()

def sendMail(priceMin,priceMax,productName,price,mail,site,pic,name):
    #sendMail(productName,mail,name)
    import email.message
    msg=email.message.EmailMessage()
    msg["From"]="mrcrawler987@gmail.com"
    msg["To"]=mail
    msg["Subject"]=productName

    #純文字內容
    if priceMin=="":
        msg.add_alternative("""\
        <head>
    <meta charset="UTF-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Document</title>
    </head>
    <body style="background-color: #F5F6F7;
            box-sizing: border-box;">
    <div class="content" 
        style="background: linear-gradient(130deg, #A4BFEF 50%, #6A93CB 100%);
                width:70vw;
                margin:auto;
                ">
        <p style="margin: 1rem;
                padding: 1rem;
                font-weight: 500;
                font-size: 1.3rem;
                color:#000000">Hi　"""+name+""":</p>
        <h2 style="text-align: center;color:#000000">"""+productName+"""</h2>
        <h3 style="text-align: center; color:#000000">目前價格為: <span style="color: red;font-size: 1.5rem; font-weight: 700;"> $"""+price+"""</span></h3>
        <img src="https://cs-b.ecimg.tw/"""+pic+"""" alt="" 
        style="display: block;width: 35%;
               margin: auto; padding: 1rem;
               border-radius: 20px;
               object-fit:cover">
        <a href='"""+site+"""' style="display: block;
        text-align: center;
        font-size: 1.3rem;
        color:#000000;
        width: fit-content;
        margin: auto;
        background-color: #353b48;
        color: #FFFFFF;
        text-decoration: none;
        padding: .5rem 2rem;
        border-radius: 30px;">點我購買</a><br>
    </div>
        <footer style="background-color: #e3e3e3;
                        width: 70vw;
                        margin: auto;
                        padding: 2rem 0;">
            <p style="margin-left: 1rem;
                    color: #888888;
                    text-align: center;">©Copyright 2022 by Mr.crawler987 Taiwan</p>
        </footer>
            
    </body>
    </html>
            """,subtype="html")
    else: 
        msg.set_content("$"+priceMin+"~"+"$"+priceMax)
    #html內容
    
    import smtplib
    server=smtplib.SMTP_SSL("smtp.gmail.com",465)
    server.login("mrcrawler987@gmail.com","xxx")
    server.send_message(msg)
    server.close()

scheduler = BackgroundScheduler(daemon=True)
#scheduler.add_job(getSiteFromDb, 'interval', seconds=3)
scheduler.add_job(getSiteFromDb, 'cron',day_of_week='mon-sun',  hour=12, minute=00,timezone='Asia/Taipei')
scheduler.start() 

if __name__ == "__main__":
    app.run()