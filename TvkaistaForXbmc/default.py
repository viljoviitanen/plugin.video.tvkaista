import xbmcgui, urllib, urllib2 , re, os, xbmcplugin, htmlentitydefs

BASE_RESOURCE_PATH = xbmc.translatePath( os.path.join( os.getcwd(), "resources" ) )
sys.path.append( os.path.join( BASE_RESOURCE_PATH, "lib" ) )

import httplib2

from string import split, replace, find
global http
global headers
headers = {'Content-type': 'application/x-www-form-urlencoded'}
http = httplib2.Http()

# Olio tiedostomuodon kertomiseen
def bitrate(nro):
  if nro == 0:
    if xbmcplugin.getSetting("bitrate") == "0":
      return "mp4"
    elif xbmcplugin.getSetting("bitrate") == "1":
      return "flv"
    elif xbmcplugin.getSetting("bitrate") == "2":
      return "h264"
    elif xbmcplugin.getSetting("bitrate") == "3":
      return "ts"
  if nro == 1:
    if xbmcplugin.getSetting("bitrate") == "0":
      return "mp4"
    elif xbmcplugin.getSetting("bitrate") == "1":
      return "flv"
    elif xbmcplugin.getSetting("bitrate") == "2":
      return "2M.mp4"
    elif xbmcplugin.getSetting("bitrate") == "3":
      return "mp2t"


def rfc822month(mon):
  if mon == 'Jan':
    return '01'
  if mon == 'Feb':
    return '02'
  if mon == 'Mar':
    return '03'
  if mon == 'Apr':
    return '04'
  if mon == 'May':
    return '05'
  if mon == 'Jun':
    return '06'
  if mon == 'Jul':
    return '07'
  if mon == 'Aug':
    return '08'
  if mon == 'Sep':
    return '09'
  if mon == 'Oct':
    return '10'
  if mon == 'Nov':
    return '11'
  if mon == 'Dec':
    return '12'

# Korjaa htmlentityt feedeissä, suosikit ja haku
def unescape(text):
    def fixup(m):
        text = m.group(0)
        if text[:2] == "&#":
            try:
                if text[:3] == "&#x":
                    return unichr(int(text[3:-1], 16))
                else:
                    return unichr(int(text[2:-1]))
            except ValueError:
                pass
        else:
            try:
                text = unichr(htmlentitydefs.name2codepoint[text[1:-1]])
            except KeyError:
                pass
        return text
    return re.sub("&#?\w+;", fixup, text)

# Kirjautuminen, xbmc suorittaa aina skriptan uudelleen kun haetaan jotain joten kirjautuminen pitää tehdä aina. Tähän tulossa muutos.
def login(maa):
  if maa == '0':
    loginurl = 'http://www.tvkaista.fi/netpvr/Login'
    username = xbmcplugin.getSetting("username")
    password = xbmcplugin.getSetting("password")
  else:
    loginurl = 'http://se.tvkaista.fi/netpvr/Login'
    username = xbmcplugin.getSetting("sverigeusername")
    password = xbmcplugin.getSetting("sverigepassword")
  body = {'action': 'login', 'username': username, 'password': password, 'rememberme':'on'}
  global headers
  headers = {'Content-type': 'application/x-www-form-urlencoded'}
  response, content = http.request(loginurl, 'POST', headers=headers, body=urllib.urlencode(body))
  return response['set-cookie']

# Loginskripta betan toimintoja varten (ei tarvita nykyisin)
def betalogin():
  loginurl = 'http://beta.tvkaista.fi/user/login'
  username = xbmcplugin.getSetting("username")
  password = xbmcplugin.getSetting("password")
  body = {'username': username, 'password': password, 'remember_me':'0'}
  global headers
  headers = {'Content-type': 'application/x-www-form-urlencoded'}
  response, content = http.request(loginurl, 'POST', headers=headers, body=urllib.urlencode(body))
  return response['set-cookie']

# Listaa saatavilla olevat aakkoset (ei löydy samassa nipussa kaikki ohjelmat, enkä laita tätä fetchaa jokaista sivua)
def programsalphabet():
  headers['Cookie'] = login('0')
  url = 'http://www.tvkaista.fi/netpvr/ProgramList'
  response, content = http.request(url, 'GET', headers=headers)
  Temp_Web_URL = re.compile(r'<td> <a href="ProgramList[?]choice=([&;\w]*)"[style="color: red;"\s]*>[#&;\w]*</a> </td>', re.IGNORECASE).findall(content)
  Temp_Web_Name = re.compile(r'<td> <a href="ProgramList[?]choice=[&;\w]*"[style="color: red;"\s]*>([#&;\w]*)</a> </td>', re.IGNORECASE).findall(content)
#  Temp_Web_URL.pop(0)
#  Temp_Web_Name.pop(0)
  for name,url in zip(Temp_Web_Name,Temp_Web_URL):
    if name == '&Aring;':
      name = "Å"
    if name == '&Auml;':
      name = "Ä"
    if name == '&Ouml;':
      name = "Ö"
    u=sys.argv[0]+"?url="+urllib.quote_plus(url[0])+"&mode="+"5"
    listfolder = xbmcgui.ListItem(name)
    listfolder.setInfo('video', {'Title': name})
    xbmcplugin.addDirectoryItem(int(sys.argv[1]), u, listfolder, isFolder=1, totalItems=26)

# Valitun aakkosen ohjelmat
def programs(urli):
  headers['Cookie'] = login('0')
  url = 'http://www.tvkaista.fi/netpvr/ProgramList?choice=%s' % (urli)
  response, content = http.request(url, 'GET', headers=headers)
  Temp_Web_URL = re.compile(r'<a href="Search[?]searchtype=title&searchkey=&quot;(.*)&quot;&showall=incomplete&amp;pvr=\d*">.*</a>', re.IGNORECASE).findall(content)
  Temp_Web_Name = re.compile(r'<a href="Search[?]searchtype=title&searchkey=&quot;.*&quot;&showall=incomplete&amp;pvr=\d*">(.*)</a>', re.IGNORECASE).findall(content)
  for name,url in zip(Temp_Web_Name,Temp_Web_URL):
#    url = 'http://beta.tvkaista.fi%s' % (url)
    u=sys.argv[0]+"?url="+url+"&mode="+"7"
    listfolder = xbmcgui.ListItem(unicode(name, 'utf-8'))
    listfolder.setInfo('video', {'Title': unicode(name, 'utf-8')})
    xbmcplugin.addDirectoryItem(int(sys.argv[1]), u, listfolder, isFolder=1, totalItems=26)

# Valitun ohjelman ohjelmat, betakamaa, ei toiminnassa nykyisin mutta valmiina myöhempää käyttöä varten
def program(urli):
  headers['Cookie'] = betalogin()
  url = urli
  response, content = http.request(url, 'GET', headers=headers)
  Temp_Web_URL = re.compile(r"""<a href="#" onclick="Player[.]openPlayerWindow[(]'/programs/watch/(\d*)/.*', this[)]; return false;" class=".*" id="airing-\d*" rel=".*">\d*[.]\d*[.]\d* Klo \d*:\d*</a>""", re.IGNORECASE).findall(content)
  Temp_Web_Desc = re.compile(r"</h3>[\s]*<p>(.*)</p>", re.IGNORECASE).findall(content)
  Temp_Web_Name = re.compile(r"""<a href="#" onclick="Player[.]openPlayerWindow[(]'/programs/watch/\d*/.*', this[)]; return false;" class=".*" id="airing-\d*" rel=".*">(\d*[.]\d*[.]\d* Klo \d*:\d*)</a>""", re.IGNORECASE).findall(content)
  for urls,nimi,desc in zip(Temp_Web_URL,Temp_Web_Name,Temp_Web_Desc):
    try:
      url = 'http://beta.tvkaista.fi/program/ajaxDetails/%s' % (urls)
      response, content = http.request(url, 'GET', headers=headers)
      Temp_Web_URL = re.compile(r'<a href="/programs/download/\d*/.*_(\d*)[.][flvmp42mmp2t.]*">Lataa</a>', re.IGNORECASE).findall(content)
#      Temp_Web_Thumb = re.compile(r'<img src="/program/thumbnail/(\d*)" class="lazy thumbnail" />', re.IGNORECASE).findall(content)
      Temp_Web_Day = re.compile(r"(\d*)[.]\d*[.]\d* Klo \d*:\d*", re.IGNORECASE).findall(nimi)
      Temp_Web_Month = re.compile(r"\d*[.](\d*)[.]\d* Klo \d*:\d*", re.IGNORECASE).findall(nimi)
      Temp_Web_Year = re.compile(r"\d*[.]\d*[.](\d*) Klo \d*:\d*", re.IGNORECASE).findall(nimi)
      progurl = Temp_Web_URL[0]
#      thumburl = Temp_Web_Thumb[0]
      xbdate = '%s-%s-%s' % (Temp_Web_Year[0],Temp_Web_Month[0],Temp_Web_Day[0])
      urlii = 'http://%s:%s@%s%s.%s' % (urllib.quote(xbmcplugin.getSetting("username")), urllib.quote(xbmcplugin.getSetting("password")), 'www.tvkaista.fi/netpvr/Download/', progurl, bitrate(0))
#      if xbmcplugin.getSetting("dlsearchthumbs") == 'true':
#        thumbi = 'http://%s:%s@%s%s' % (urllib.quote(xbmcplugin.getSetting("username")), urllib.quote(xbmcplugin.getSetting("password")), 'beta.tvkaista.fi/program/thumbnail/', urls)
#        listitem = xbmcgui.ListItem(unicode(nimi, 'utf-8'), iconImage="DefaultVideo.png", thumbnailImage=thumbi)
#      else:
      listitem = xbmcgui.ListItem(unicode(nimi, 'utf-8'), iconImage="DefaultVideo.png")
      listitem.setInfo('video', {'Title': nimi, 'Plot': unicode(desc, 'utf-8'), 'Date': xbdate})
      xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=urlii,listitem=listitem)
    except:
      pass
  xbmcplugin.addSortMethod(int(sys.argv[1]), xbmcplugin.SORT_METHOD_DATE)

#Betakamaa
def watchlist():
  headers['Cookie'] = betalogin()
  url = 'http://beta.tvkaista.fi/watchlist'
  response, content = http.request(url, 'GET', headers=headers)
  Temp_Web_URL = re.compile(r"""<div class="watchlist-program-name"><a href="#" onclick="Player[.]openPlayerWindow[(]'/programs/watch/(\d*)/.*', this[)]; return false;" class=".*" id="airing-\d*" rel=".*">.*</a></div>""", re.IGNORECASE).findall(content)
  Temp_Web_Name = re.compile(r"""<div class="watchlist-program-name"><a href="#" onclick="Player[.]openPlayerWindow[(]'/programs/watch/\d*/.*', this[)]; return false;" class=".*" id="airing-\d*" rel=".*">(.*)</a></div>""", re.IGNORECASE).findall(content)
  Temp_Web_Desc = re.compile('<div class="watchlist-program-text">(.*)</div>', re.IGNORECASE).findall(content)
  Temp_Web_Date = re.compile(r'<div class="watchlist-program-date">(\d*[.]\d*[.]\d* klo \d*:\d*) - .*</div>', re.IGNORECASE).findall(content)
  Temp_Web_Time = re.compile(r'<div class="watchlist-program-date">\d*[.]\d*[.]\d* klo (\d*:\d*) - .*</div>', re.IGNORECASE).findall(content)
  Temp_Web_Chan = re.compile(r'<div class="watchlist-program-date">\d*[.]\d*[.]\d* klo \d*:\d* - (.*)</div>', re.IGNORECASE).findall(content)
  for urls,nimi,desc,progdate,progchan,progklo in zip(Temp_Web_URL,Temp_Web_Name,Temp_Web_Desc,Temp_Web_Date,Temp_Web_Chan,Temp_Web_Time):
    try:
      url = 'http://beta.tvkaista.fi/program/ajaxDetails/%s' % (urls)
      response, content = http.request(url, 'GET', headers=headers)
      Temp_Web_URL = re.compile(r'<a href="/programs/download/\d*/.*_(\d*)[.][flvmp42mmp2t.]*">Lataa</a>', re.IGNORECASE).findall(content)
#      Temp_Web_Thumb = re.compile(r'<img src="/program/thumbnail/(\d*)" class="lazy thumbnail" />', re.IGNORECASE).findall(content)
      Temp_Web_Day = re.compile(r"(\d*)[.]\d*[.]\d* Klo \d*:\d*", re.IGNORECASE).findall(progdate)
      Temp_Web_Month = re.compile(r"\d*[.](\d*)[.]\d* Klo \d*:\d*", re.IGNORECASE).findall(progdate)
      Temp_Web_Year = re.compile(r"\d*[.]\d*[.](\d*) Klo \d*:\d*", re.IGNORECASE).findall(progdate)
      progurl = Temp_Web_URL[0]
      thumburl = Temp_Web_Thumb[0]
      xbdate = '%s-%s-%s' % (Temp_Web_Year[0],Temp_Web_Month[0],Temp_Web_Day[0])
      urlii = 'http://%s:%s@%s%s.%s' % (urllib.quote(xbmcplugin.getSetting("username")), urllib.quote(xbmcplugin.getSetting("password")), 'www.tvkaista.fi/netpvr/Download/', progurl, bitrate(0))
#      thumbi = 'http://%s:%s@%s%s' % (urllib.quote(xbmcplugin.getSetting("username")), urllib.quote(xbmcplugin.getSetting("password")), 'beta.tvkaista.fi/program/thumbnail/', thumburl)
      nimike = '%s %s | %s (%s)' % (xbdate, progklo,nimi,progchan)
#      if xbmcplugin.getSetting("dlwatchlthumbs") == 'true':
#        listitem = xbmcgui.ListItem(unicode(nimike, 'utf-8'), iconImage="DefaultVideo.png", thumbnailImage=thumbi)
#     else:
      listitem = xbmcgui.ListItem(unicode(nimike, 'utf-8'), iconImage="DefaultVideo.png")
      listitem.setInfo('video', {'Title': nimike, 'Plot': unicode(desc, 'utf-8'), 'Date': xbdate})
      xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=urlii,listitem=listitem)
    except:
      pass
  xbmcplugin.addSortMethod(int(sys.argv[1]), xbmcplugin.SORT_METHOD_DATE)

def history():
  headers['Cookie'] = betalogin()
  url = 'http://beta.tvkaista.fi/history/all'
  response, content = http.request(url, 'GET', headers=headers)
  Temp_Web_URL = re.compile(r'<td><a href="/programs/details/(\d*/.*)">.*</a></td>', re.IGNORECASE).findall(content)
  Temp_Web_Name = re.compile(r'<td><a href="/programs/details/\d*/.*">(.*)</a></td>', re.IGNORECASE).findall(content)
  Temp_Web_Lastseen = re.compile(r"""<td><a href="#" onclick="Player[.]openPlayerWindow[(]'/programs/watch/\d*/.*', this[)]; return false;" class="show-program-details-box airing-link" id="airing-\d*" rel="pro mobile full normal">(\d*[.]\d*[.]\d* \d*:\d*)</a></td>""", re.IGNORECASE).findall(content)
  for urls,lastseen,name in zip(Temp_Web_URL,Temp_Web_Lastseen,Temp_Web_Name):
    Temp_Web_Day = re.compile(r"(\d*)[.]\d*[.]\d* \d*:\d*", re.IGNORECASE).findall(lastseen)
    Temp_Web_Month = re.compile(r"\d*[.](\d*)[.]\d* \d*:\d*", re.IGNORECASE).findall(lastseen)
    Temp_Web_Year = re.compile(r"\d*[.]\d*[.](\d*) \d*:\d*", re.IGNORECASE).findall(lastseen)
    xbdate = '%s-%s-%s' % (Temp_Web_Year[0],Temp_Web_Month[0],Temp_Web_Day[0])
    name = '%s (Viimeksi katsottu %s)' % (name,lastseen)
    urls = 'http://beta.tvkaista.fi/programs/details/%s' % (urls)
    u=sys.argv[0]+"?url="+urls+"&mode="+"7"
    listitem = xbmcgui.ListItem(unicode(name, 'utf-8'), iconImage="DefaultVideo.png")
    listitem.setInfo('video', {'Title': name, 'Date': xbdate})
    xbmcplugin.addDirectoryItem(int(sys.argv[1]), u, listitem, isFolder=1)
  xbmcplugin.addSortMethod(int(sys.argv[1]), xbmcplugin.SORT_METHOD_DATE)

# Maanvalinta, jos käyttäjätiedot on merkattu molempiin
def selection():
  if xbmcplugin.getSetting("username") != '' and xbmcplugin.getSetting("password") != '' and xbmcplugin.getSetting("sverigepassword") != '' and xbmcplugin.getSetting("sverigeusername") != '':
    u=sys.argv[0]+"?url="+urllib.quote_plus('Suomi')+"&mode="+"4"+"&maa="+"0"
    listfolder = xbmcgui.ListItem('TVkaista Suomi')
    listfolder.setInfo('video', {'Title': 'TVkaista Suomi'})
    xbmcplugin.addDirectoryItem(int(sys.argv[1]), u, listfolder, isFolder=1)
    u=sys.argv[0]+"?url="+urllib.quote_plus('Sverige')+"&mode="+"4"+"&maa="+"1"
    listfolder = xbmcgui.ListItem('TVkaista Sverige')
    listfolder.setInfo('video', {'Title': 'TVkaista Sverige'})
    xbmcplugin.addDirectoryItem(int(sys.argv[1]), u, listfolder, isFolder=1)
  elif xbmcplugin.getSetting("username") != '' and xbmcplugin.getSetting("password") != '':
    dates('0')
  elif xbmcplugin.getSetting("sverigeusername") != '' and xbmcplugin.getSetting("sverigepassword") != '':
    dates('1')
  else:
    u=sys.argv[0]
    listfolder = xbmcgui.ListItem('Jokin on vialla, tarkista asetukset')
    listfolder.setInfo('video', {'Title': 'Jokin on vialla, tarkista asetukset'})
    xbmcplugin.addDirectoryItem(int(sys.argv[1]), u, listfolder, isFolder=1)

# Listaa päivämäärät ja haku/suosikit kohdat
def dates(maa):
  headers['Cookie'] = login(maa)
  if maa == '0':
    url = 'http://www.tvkaista.fi/netpvr/Recordings'
  if maa == '1':
    url = 'http://se.tvkaista.fi/netpvr/Recordings'
  response, content = http.request(url, 'GET', headers=headers)
  Temp_Web_DATEURL = re.compile(r'href="Recordings[?]action=setdate&amp;date=([\d.]*)&amp;pvr=\d*">[^<]', re.IGNORECASE).findall(content)
  for datename in Temp_Web_DATEURL:
    paiva = re.compile('(\d*)[.]\d*[.]\d*', re.IGNORECASE).findall(datename)
    kuukausi = re.compile('\d*[.](\d*)[.]\d*', re.IGNORECASE).findall(datename)
    vuosi = re.compile('\d*[.]\d*[.](\d*)', re.IGNORECASE).findall(datename)
    paivamaara = '%s-%s-%s' % (vuosi[0],kuukausi[0],paiva[0])
    u=sys.argv[0]+"?url="+urllib.quote_plus(datename)+"&mode="+"1"+"&maa="+str(maa)
    listfolder = xbmcgui.ListItem(paivamaara)
    listfolder.setInfo('video', {'Title': paivamaara})
    xbmcplugin.addDirectoryItem(int(sys.argv[1]), u, listfolder, isFolder=1, totalItems=14)
  u=sys.argv[0]+"?url="+urllib.quote_plus('Varasto')+"&mode="+"2"+"&maa="+str(maa)
  listfolder = xbmcgui.ListItem('Varasto')
  listfolder.setInfo('video', {'Title': 'Varasto'})
  xbmcplugin.addDirectoryItem(int(sys.argv[1]), u, listfolder, isFolder=1)
  u=sys.argv[0]+"?url="+urllib.quote_plus('Haku')+"&mode="+"3"+"&maa="+str(maa)
  listfolder = xbmcgui.ListItem('Haku')
  listfolder.setInfo('video', {'Title': 'Haku'})
  xbmcplugin.addDirectoryItem(int(sys.argv[1]), u, listfolder, isFolder=1)
  u=sys.argv[0]+"?url="+urllib.quote_plus('Sarjat')+"&mode="+"10"+"&maa="+str(maa)
  listfolder = xbmcgui.ListItem('Sarjat')
  listfolder.setInfo('video', {'Title': 'Sarjat'})
  xbmcplugin.addDirectoryItem(int(sys.argv[1]), u, listfolder, isFolder=1)
  if maa == '0':
    u=sys.argv[0]+"?url="+urllib.quote_plus('Ohjelmat')+"&mode="+"6"
    listfolder = xbmcgui.ListItem('Ohjelmat')
    listfolder.setInfo('video', {'Title': 'Ohjelmat'})
    xbmcplugin.addDirectoryItem(int(sys.argv[1]), u, listfolder, isFolder=1)
#    Betakamaa!
#    u=sys.argv[0]+"?url="+urllib.quote_plus('Historia')+"&mode="+"8"
#    listfolder = xbmcgui.ListItem('Historia')
#    listfolder.setInfo('video', {'Title': 'Historia'})
#    xbmcplugin.addDirectoryItem(int(sys.argv[1]), u, listfolder, isFolder=1)
    u=sys.argv[0]+"?url="+urllib.quote_plus('Lista')+"&mode="+"9"+"&maa="+str(maa)
    listfolder = xbmcgui.ListItem('Lista')
    listfolder.setInfo('video', {'Title': 'Lista'})
    xbmcplugin.addDirectoryItem(int(sys.argv[1]), u, listfolder, isFolder=1)
  headers['Cookie'] = None

# Parsee käynnistysparametrit kun skriptaa suoritetaan uudelleen
def get_params():
  param=[]
  paramstring=sys.argv[2]
  if len(paramstring)>=2:
      params=sys.argv[2]
      cleanedparams=params.replace('?','')
      if (params[len(params)-1]=='/'):
        params=params[0:len(params)-2]
      pairsofparams=cleanedparams.split('&')
      param={}
      for i in range(len(pairsofparams)):
        splitparams={}
        splitparams=pairsofparams[i].split('=')
        if (len(splitparams))==2:
          param[splitparams[0]]=splitparams[1]
  return param

# Listaa päivämäärän ohjelmat
def recordings(url, maa):
  headers['Cookie'] = login(maa)
  if maa == '0':
    curl = 'www.tvkaista.fi/'
    username = xbmcplugin.getSetting("username")
    password = xbmcplugin.getSetting("password")
  else:
    curl = 'se.tvkaista.fi/'
    username = xbmcplugin.getSetting("sverigeusername")
    password = xbmcplugin.getSetting("sverigepassword")
  dateurl = 'http://%snetpvr/Recordings?action=setdate&date=%s' % (curl,url)
  showdate = url
  response, content = http.request(dateurl, 'GET', headers=headers)
  Temp_Web_URL = re.compile(r"""return popupRecording[(](\d*),'flv'[)];">[^<>]*</a>""", re.IGNORECASE).findall(content)
  Temp_Web_Name = re.compile(r"""return popupRecording[(]\d*,'flv'[)];">([^<>]*)</a>""", re.IGNORECASE).findall(content)
  for urls,nimi in zip(Temp_Web_URL,Temp_Web_Name):
    urlii = 'http://%s:%s@%snetpvr/Download/%s.%s' % (urllib.quote(username), urllib.quote(password), curl, urls, bitrate(0))
#    thumbi = 'http://%s:%s@%s%s' % (urllib.quote(xbmcplugin.getSetting("username")), urllib.quote(xbmcplugin.getSetting("password")), 'beta.tvkaista.fi/program/thumbnail/', urls)
#    if xbmcplugin.getSetting("dldatethumbs") == 'true' and maa == '0':
#      listitem = xbmcgui.ListItem(unicode(nimi, 'utf-8'), iconImage="DefaultVideo.png", thumbnailImage=thumbi)
#    else:
    listitem = xbmcgui.ListItem(unicode(nimi, 'utf-8'), iconImage="DefaultVideo.png")
    listitem.setInfo('video', {'Title': unicode(nimi, 'utf-8'), 'Date': url[0]})
    xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=urlii,listitem=listitem)

# Listaa suosikit
def favorites():
  headers['Cookie'] = login(maa)
  if str(maa) == '0':
    curl = 'www.tvkaista.fi/'
    username = xbmcplugin.getSetting("username")
    password = xbmcplugin.getSetting("password")
  else:
    curl = 'se.tvkaista.fi/'
    username = xbmcplugin.getSetting("sverigeusername")
    password = xbmcplugin.getSetting("sverigepassword")
  favurl = 'http://%snetpvr/Feed?channel=Playlist&format=mp4&extension=itunes' % (curl)
  response, content = http.request(favurl, 'GET', headers=headers)
  feedreader(content, xbmcplugin.getSetting("username"), xbmcplugin.getSetting("password"))

def storage():
  headers['Cookie'] = login(maa)
  if str(maa) == '0':
    curl = 'www.tvkaista.fi/'
    username = xbmcplugin.getSetting("username")
    password = xbmcplugin.getSetting("password")
  else:
    curl = 'se.tvkaista.fi/'
    username = xbmcplugin.getSetting("sverigeusername")
    password = xbmcplugin.getSetting("sverigepassword")
  favurl = 'http://%snetpvr/Feed?channel=favourites&format=mp4&extension=itunes' % (curl)
  response, content = http.request(favurl, 'GET', headers=headers)
  feedreader(content, xbmcplugin.getSetting("username"), xbmcplugin.getSetting("password"))

# TODO: Ohjelmacache, tällä hetkellä se saa ohjelmien id:tkin mutta koska xbmc:n plugarit toimivat niin että ne tekevät jonkun homman ja sulkeutuu niin ne menetetään tällä hetkellä
def seasonpass():
  headers['Cookie'] = login(maa)
  url = 'http://www.tvkaista.fi/netpvr/SeasonPass'
  response, content = http.request(url, 'GET', headers=headers)
  Temp_Web_URL = re.compile('<h1 style="Font-size:15px;Font-weight:bold;">(.*)</h1>', re.IGNORECASE).findall(content)
  for name in Temp_Web_URL:
    u=sys.argv[0]+"?url="+name+"&mode="+"7"
    listitem = xbmcgui.ListItem(unicode(name, 'utf-8'), iconImage="DefaultVideo.png")
    listitem.setInfo('video', {'Title': name})
    xbmcplugin.addDirectoryItem(int(sys.argv[1]), u, listitem, isFolder=1)
  xbmcplugin.addSortMethod(int(sys.argv[1]), xbmcplugin.SORT_METHOD_DATE)


def feedreader(result, username, password):
  Temp_Web_URL = re.compile(r'<enclosure url="http://[.\w]*tvkaista[.]fi/netpvr/Download/(\d*)[.]mp4"', re.IGNORECASE).findall(result)
  Temp_Web_Date = re.compile('<pubDate>(.*) [+]\d*</pubDate>', re.IGNORECASE).findall(result)
  Temp_Web_Name = re.compile('<item>\s*<title>(.*)</title>', re.IGNORECASE).findall(result)
  Temp_Web_Channel = re.compile('<itunes:author>(.*)</itunes:author>', re.IGNORECASE).findall(result)
  Temp_Web_Desc = re.compile('<description>(.*)</description>', re.IGNORECASE).findall(result)
  Temp_Web_Length = re.compile('<itunes:duration>(.*)</itunes:duration>', re.IGNORECASE).findall(result)
  Temp_Web_Desc.pop(0)
  Temp_Web_Channel.remove('TVkaista NetPVR')
  Temp_Web_Date.pop(0)
  for progurl,progdate,progname,progchan,proglength,progdesc in zip(Temp_Web_URL,Temp_Web_Date,Temp_Web_Name,Temp_Web_Channel,Temp_Web_Length,Temp_Web_Desc):
    progname = progname.replace('&apos;', "'")
    progdesc = progdesc.replace('&apos;', "'")
    year = re.compile(r"\w*, \d* \w* (\d*) \d*:\d*:\d*", re.IGNORECASE).findall(progdate)
    month = re.compile(r"\w*, \d* (\w*) \d* \d*:\d*:\d*", re.IGNORECASE).findall(progdate)
    day = re.compile(r"\w*, (\d*) \w* \d* \d*:\d*:\d*", re.IGNORECASE).findall(progdate)
    clocktime = re.compile(r"\w*, \d* \w* \d* (\d*:\d*:\d*)", re.IGNORECASE).findall(progdate)
    xbdate = '%s-%s-%s' % (year[0], rfc822month(month[0]), day[0])
    urlii = 'http://%s:%s@%snetpvr/Download/%s.%s' % (urllib.quote(username), urllib.quote(password),'tvkaista.fi/', progurl, bitrate(0))
    nimike = '%s %s | %s (%s)' % (xbdate, clocktime[0],unescape(progname),progchan)
 #   if xbmcplugin.getSetting("dlfavthumbs") == 'true' and maa == '0':
 #     thumbi = 'http://%s:%s@%s%s.jpg' % (urllib.quote(xbmcplugin.getSetting("username")), urllib.quote(xbmcplugin.getSetting("password")), 'tvkaista.fi/netpvr/resources/recordings/screengrabs/', progurl)
 #     listitem = xbmcgui.ListItem(nimike, iconImage="DefaultVideo.png", thumbnailImage=thumbi)
 #   else:
    listitem = xbmcgui.ListItem(nimike, iconImage="DefaultVideo.png")
    listitem.setInfo('video', {'Title': nimike, 'Plot': unescape(progdesc), 'Duration': proglength, 'Date': xbdate})
    xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=urlii,listitem=listitem)
  xbmcplugin.addSortMethod(int(sys.argv[1]), xbmcplugin.SORT_METHOD_DATE)

# Antaa käyttäjälle virtuaalisen näppäimistön ja listaa hakutulokset
def search(maa):
#  headers['Cookie'] = login(maa)
  keyboard = xbmc.Keyboard()
  keyboard.doModal()
  if (keyboard.isConfirmed()):
    searchresult(keyboard.getText(), maa)

def searchresult(hakusana, maa):
  nappaimisto = hakusana
  nappaimisto = urllib.quote_plus(hakusana)
  headers['Cookie'] = login(maa)
  if maa == '0':
    curl = 'http://www.tvkaista.fi/'
    username = xbmcplugin.getSetting("username")
    password = xbmcplugin.getSetting("password")
  else:
    curl = 'http://se.tvkaista.fi/'
    username = xbmcplugin.getSetting("sverigeusername")
    password = xbmcplugin.getSetting("sverigepassword")
  favurl = '%snetpvr/Feed?channel=search&search=%s&format=mp4&extension=itunes' % (curl, nappaimisto)
  response, content = http.request(favurl, 'GET', headers=headers)
  feedreader(content, xbmcplugin.getSetting("username"), xbmcplugin.getSetting("password"))

params=get_params()
url=None
name=None
mode=None
headers=None
maa=None
try:
        url=urllib.unquote_plus(params["url"])
except:
        pass
try:
        name=urllib.unquote_plus(params["name"])
except:
        pass
try:
        mode=int(params["mode"])
except:
        pass
try:
        headers=int(params["headers"])
except:
        pass
try:
        maa=str(params["maa"])
except:
        pass

if mode==None or url==None or len(url)<1:
        selection()
        
elif mode==1:
        recordings(url, maa)

elif mode==2:
        storage()

elif mode==3:
        search(maa)

elif mode==4:
        dates(maa)

elif mode==5:
        programs(url)

elif mode==6:
        programsalphabet()

elif mode==7:
        url = '"%s"' % url
        searchresult(url, '0')

elif mode==8:
        history()

elif mode==9:
        favorites()

elif mode==10:
        seasonpass()

# Kaikki kunnossa, ilmoitetaan että tässä oli kaikki
xbmcplugin.endOfDirectory(int(sys.argv[1]))