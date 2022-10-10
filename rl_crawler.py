
import mysql.connector
import os,sys,re,time
from urllib.request import urlopen
from bs4 import BeautifulSoup
from collections import defaultdict



### This function fills the database with the object information and prices from rl.insider.gg/pc
def fill_db(bp=False):

    file_name=r'\Users\flori\Desktop\insider.html'
    price_table="item_prices"
    if(bp):
        file_name=r'\Users\flori\Desktop\bp_insider.html'
        price_table="bp_prices"

    f = open(r'\Users\flori\Desktop\bp_insider.html',encoding="UTF-8")
    html=f.read()
    prices_html = BeautifulSoup(html)

    try:
        cnx = mysql.connector.connect(user='root', password='',
                                host='127.0.0.1',
                                database='rltrader')
    except mysql.connector.Error as err:
        print(err)
    cursor = cnx.cursor()

    types_id={}
    query = ("SELECT id,rl_insider_name FROM item_type")
    cursor.execute(query)
    for (id,name) in cursor:
        types_id[name]=id
    types_id["alphaBeta"]=None

    rarities_id={}
    query = ("SELECT id,name FROM item_rarity")
    cursor.execute(query)
    for (id,name) in cursor:
        rarities_id[name]=id
    rarities_id[False]=None

    tables = prices_html.body.find_all("table",attrs={'class':'priceTable'})

    for table in tables:
        painted=False
        if("unpainted" not in table['id']):
            if("painted" in table['id']):
                painted=True
        type=table['id'].replace("unpainted","").replace("painted","").replace("Prices","")
        rarity=False
        if("Wheels" in type):
            rarity=type.replace("Wheels","").lower()
            if(rarity=="veryrare"):
                rarity="very_rare"
            if(rarity==""):
                rarity=False
            type="Wheels"
        if("BM" in type):
            rarity="black_market"
            type=type[2:]


        if(type=="alphaBeta"):
            continue

        print("----")
        print(table['id'])
        print(type)
        print(types_id[type])
        print(rarities_id[rarity])

        items=table.find_all("tr")
        for item in items:
            id_rl_insider=0
            try:
                id_rl_insider=item['data-iid']
            except:
                continue

            item_name=item.find("div").text
            print(item_name)

            query="SELECT id_rl_insider FROM item WHERE id_rl_insider = %s"
            cursor.execute(query,(id_rl_insider, ))
            cursor.fetchall()
            if(cursor.rowcount==0):
                print("INSERT "+id_rl_insider+" "+item_name+" "+str(types_id[type])+" "+str(rarities_id[rarity]))
                query="INSERT INTO item(id,name,type,rarity,id_rl_insider) VALUES(%s,%s,%s,%s)"
                cursor.execute(query,(id_rl_insider,item_name,types_id[type],rarities_id[rarity],))


            query="SELECT * FROM {} WHERE id_rl_insider = %s".format(price_table)
            cursor.execute(query,(id_rl_insider, ))
            cursor.fetchall()
            if(cursor.rowcount>0):
                continue

            #colors = ['default','Black','White','Grey','Crimson','Pink','Cobalt','Sky Blue','Sienna','Saffron','Lime','Green','Orange','Purple','Gold']

            prices=[[None,None],[None,None],[None,None],[None,None],[None,None],[None,None],[None,None],[None,None],[None,None],[None,None],[None,None],[None,None],[None,None],[None,None],[None,None]]

            cpt=-1
            for price in item.children:
                if(cpt>=0):
                    prices[cpt]=price.string.split("-")
                    prices[cpt][0]=prices[cpt][0].replace("\u200a","")
                    prices[cpt][0]=prices[cpt][0].replace("\u2003","—")
                    if(len(prices[cpt])>1):
                        prices[cpt][1]=prices[cpt][1].replace("\u200a","")
                        if("k" in prices[cpt][1]):
                            prices[cpt][0]=str(int(float(prices[cpt][0])*1000))
                            prices[cpt][1]=str(int(float(prices[cpt][1][:1])*1000))
                    else:
                        prices[cpt]=[None,None]
                cpt+=1

            query="INSERT INTO {} VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)".format(price_table)
            cursor.execute(query,(id_rl_insider,prices[0][0],prices[0][1],prices[1][0],prices[1][1],prices[2][0],prices[2][1],prices[3][0],prices[3][1],prices[4][0],prices[4][1],prices[5][0],prices[5][1],prices[6][0],prices[6][1],prices[7][0],prices[7][1],prices[8][0],prices[8][1],prices[9][0],prices[9][1],prices[10][0],prices[10][1],prices[11][0],prices[11][1],prices[12][0],prices[12][1],prices[13][0],prices[13][1],prices[14][0],prices[14][1],))

    cursor.close()
    cnx.close()

    if(bp==False):
        fill_db(True)

### FILL INVENTORY #######################################################################################################

def fill_inventory():
    for i in range(8):
        fill_inventory_category(i)

def fill_inventory_category(item_type):
    file_name=r'\Users\flori\Desktop\rl_'
    if(item_type==0):
        file_name+='decals'
    elif(item_type==1):
        file_name+='goal_explosions'
    elif(item_type==2):
        file_name+='bodies'
    elif(item_type==3):
        file_name+='wheels'
    elif(item_type==4):
        file_name+='boosts'
    elif(item_type==5):
        file_name+='toppers'
    elif(item_type==7):
        file_name+='trails'
    else:
        return
    file_name+='.html'

    #init db
    try:
        cnx = mysql.connector.connect(user='root', password='',
                                host='127.0.0.1',
                                database='rltrader')
    except mysql.connector.Error as err:
        print(err)
    cursor = cnx.cursor()

    #Open file
    f = open(file_name,encoding="UTF-8")
    html = f.read()
    parsed_html = BeautifulSoup(html)

    items = parsed_html.find_all("div",attrs={'class':'rlg-item'})

    query = ("DELETE garage FROM garage inner join item on garage.id_rl_com=item.id_rl_com WHERE item.type=%s")
    cursor.execute(query, (item_type,))
    #For each item (of the given type) in my garage
    for item in items:
        #init item data
        qty = item['data-quantity']
        name = str(item.find("h2").text).replace(" Blueprint","")
        bp = item['data-blueprint']
        rarity = item['data-rarityid']
        id_rl_com = item['data-item']
        color_id = item['data-paint']

        serie=None
        certification=None
        if(item.find("div",attrs={'class':'rlg-item__cert'})):
            certification = item.find("div",attrs={'class':'rlg-item__cert'}).text.strip()
        if(item.find("div",attrs={'class':'rlg-item__series'})):
            serie = item.find("div",attrs={'class':'rlg-item__series'}).text.strip()

        #Update my garage
        query = ("DELETE FROM garage WHERE id_rl_com=%s AND color=%s AND serie=%s AND certification = %s AND is_bp=%s")
        cursor.execute(query, (id_rl_com,color_id,serie,certification,bp=="true",))
        query = ("INSERT INTO garage VALUES (%s,%s,%s,%s,%s,%s)")
        cursor.execute(query, (id_rl_com,color_id,serie,certification,bp=="true",qty,))


        #format name for decals
        if(item_type==0):
            name=name.replace(" (Global)","").replace("(","[").replace(")","]")

        query = ("SELECT id_rl_insider FROM item WHERE name like %s AND type=%s")
        cursor.execute(query, (name,item_type,))
        ids_rl_insider=cursor.fetchall()
        if(cursor.rowcount==1):
            query= ("UPDATE item set id_rl_com=%s, rarity=%s WHERE id_rl_insider=%s")
            cursor.execute(query, (id_rl_com,rarity,ids_rl_insider[0][0],))
        elif(cursor.rowcount>=2):
            query= ("UPDATE item set id_rl_com=%s WHERE name like %s AND type=%s AND rarity=%s")
            cursor.execute(query, (id_rl_com,name,item_type,rarity,))
        else:
            print(str(cursor.rowcount)+" items for "+name)

### FIND DEALS ##########################################################################################################

def find_deals(sleep_time=2,skip=-1,debug=False):
    #configurable parameters
    #sleep_time = seconds between each offer search
    #skip = skip until the {skip}th items of my garage
    #debug= True => search for only 1 item

    banned_users=["kkx178"]

    #Create connection to database
    try:
        cnx = mysql.connector.connect(user='root', password='',
                                host='127.0.0.1',
                                database='rltrader')
    except mysql.connector.Error as err:
        print(err)
        return
    cursor = cnx.cursor(buffered=True)
    cursor2 = cnx.cursor(buffered=True)

    #Init arrays color_id -> color_name, formated_color_name
    paint={}
    formated_paint={}
    query = ("SELECT * FROM paint")
    cursor.execute(query)
    for (pid,name,formated_name) in cursor:
        paint[pid]=name
        formated_paint[pid]=formated_name

    #Init array rarity_id -> rarity_name
    rarities={}
    query = ("SELECT * FROM item_rarity")
    cursor.execute(query)
    for (rid,name) in cursor:
        rarities[rid]=name

    #find all items of my collection
    query = ("SELECT DISTINCT id_rl_com,color,is_bp FROM garage")
    cursor.execute(query)
    print(cursor.rowcount)
    current=0;
    #For each item of my collection (of the given type)
    for (id_rl_com,color_id,bp) in cursor:
        current+=1
        if(current<skip):
            continue

        color=paint[color_id]
        formated_color=formated_paint[color_id]
        #find item name in db
        query = ("SELECT name, rarity FROM item WHERE id_rl_com=%s")
        cursor2.execute(query,(id_rl_com,))
        try:
            (name, rarity) = cursor2.fetchone()
        except:
            print("["+str(current)+"]no item with id_rl_com="+str(id_rl_com)+" in the db")#probably cause it's not a tradeable item
            continue

        #Delete offers stored for this item (same id[rarity] and color and bp)
        query = ("DELETE FROM offer WHERE offer.id_rl_com=%s AND offer.color=%s AND offer.is_bp=%s")
        cursor2.execute(query,(id_rl_com,color_id,bp))

        #Chose price table to look into (depending on if the item is blueprint or not)
        price_table="item_prices"
        if(bp==1):
            price_table="bp_prices"
            bp="2"#useful for the link to search later on
        else:
            bp="1"#useful for the link to search later on

        #Check the min price of this item(color,blueprint) if min_price not found then skip (item not tradeable, or bug)
        min=None
        max=None
        query = "SELECT {} FROM item INNER JOIN "+price_table+" as p on item.id_rl_insider=p.id_rl_insider WHERE item.id_rl_com=%s"
        cursor2.execute(query.format(color+"_min, "+color+"_max"), (id_rl_com,))
        try:
            (min,max)=cursor2.fetchone()
        except:
            print("\n["+str(current)+"] id_rl_com="+str(id_rl_com)+" not found in database")
            continue
        if(min==None):
            print("["+str(current)+"]no price for item["+str(id_rl_com)+",color:"+color+"]")
            continue

        #Search actual offers online for this item(id,color,min_price,bp)
        cid=str(color_id)
        if(cid=="0"):
            cid="N"
        f=urlopen("https://rocket-league.com/trading?filterItem="+str(id_rl_com)+"&filterCertification=N&filterPaint="+cid+"&filterSeries=A&filterMinCredits="+str(min)+"&filterMaxCredits=100000&filterPlatform%5B%5D=1&filterSearchType=2&filterItemType="+str(bp))
        html=f.read()
        offers_html = BeautifulSoup(html)
        trades = offers_html.body.find_all("div",attrs={"class":"rlg-trade"});

        #print item (id,name,color,min/max price,nb_offers_found)
        isbp=""
        if(bp=="2"):
            isbp="[bp]"
        print("\n--------------------")
        print("["+str(current)+"]"+isbp+name+" ("+color+", id_rl_com="+str(id_rl_com)+") | "+str(min)+" - "+str(max)+"Cr | "+str(len(trades))+" trade offers")#limit nb offers==40

        #For each offer found:
        for trade in trades:
            username = trade.find("img",attrs={"class":"rlg-trade__avatarimage"}).attrs["alt"].strip()
            if username in banned_users:
                print(username+" is banned from my list")
                continue

            try:
                offer_date = trade.find("span",attrs={"class":"rlg-trade__time"}).contents[1].text.strip()
            except:
                offer_date = "No date found"

            serie=None
            certification=None

            #Search at what place is the item
            wants = trade.find("div",attrs={"class":"rlg-trade__itemswants"})
            cpt=-1
            ok=False
            for wanted in wants.children:
                if(len(wanted)<=1):
                    continue
                cpt+=1

                #Check item name
                nametmp=name.replace("[","(").replace("]",")")#stored in db with [], exists on rl_com with ()
                if(bp=="2"):
                    nametmp+=" Blueprint"
                if(wanted.find("h2").text!=nametmp):
                    continue

                #Check item rarity
                offer_rarity=wanted.find("div",attrs={'class':'rlg-item__gradient'})['class'][1][2:].replace("-","_")
                if(offer_rarity!=rarities[rarity]):
                    continue

                #Check item color
                if(color_id==0):#default color
                    if(wanted.find("div",attrs={'class':'rlg-item__paint'})):
                        continue
                else:
                    if(not wanted.find("div",attrs={'class':'rlg-item__paint'})):
                        continue
                    col=wanted.find("div",attrs={'class':'rlg-item__paint'})
                    if(col['data-name']!=formated_color):
                        continue

                #fill Serie
                if(wanted.find("div",attrs={'class':'rlg-item__series'})):
                    serie=wanted.find("div",attrs={'class':'rlg-item__series'}).text.strip()
                if(wanted.find("div",attrs={'class':'rlg-item__cert'})):
                    certification=wanted.find("div",attrs={'class':'rlg-item__cert'}).text.strip()

                ok=True
                break
            #If item not found, skip offer
            if(not ok):
                print("item not found in trade")
                continue

            #Search offer at same place as the item
            has = trade.find("div",attrs={"class":"rlg-trade__itemshas"})
            cpttmp=cpt+1
            final_offer=None
            for ha in has:
                if(len(ha)<=1):
                    continue
                if(cpt==0):
                    try:
                        final_offer=ha.find("div",attrs={"class":"rlg-item__quantity"}).text[1:]
                    except:
                        pass
                    break
                cpt-=1

            #Insert offer into database
            query = "INSERT INTO offer(id_rl_com,color,is_bp,price,username,serie,certification,date_found,offer_date) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s)"
            cursor2.execute(query,(id_rl_com,color_id,bp=="2",final_offer,username,serie,certification,round(time.time()),offer_date,))
            if(final_offer==None):
               print("offer not found ("+username+") ("+str(cpttmp)+"e item)")
            else:
               print(final_offer+"Cr ("+username+") ("+str(cpttmp)+"e item)")

        time.sleep(sleep_time)
        if(debug):
            return

    cursor.close()
    cnx.close()

fill_db()
#fill_inventory()
#find_deals(2,1494)