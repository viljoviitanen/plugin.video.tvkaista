#xbmc alpha tvkaista plugin
#
#Copyright (C) 2009  Viljo Viitanen <viljo.viitanen@iki.fi>
#Copyright (C) 2008-2009  J. Luukko
#
#This program is free software; you can redistribute it and/or
#modify it under the terms of the GNU General Public License
#as published by the Free Software Foundation; either version 2
#of the License, or (at your option) any later version.
#
#This program is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#GNU General Public License for more details.
#
#You should have received a copy of the GNU General Public License
#along with this program; if not, write to the Free Software
#Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.

import xbmcgui, urllib, urllib2 , re, os, xbmcplugin, htmlentitydefs, time

BASE_RESOURCE_PATH = xbmc.translatePath( os.path.join( os.getcwd(), "resources" ) )
sys.path.append( os.path.join( BASE_RESOURCE_PATH, "lib" ) )

import httplib2

from string import split, replace, find
from xml.dom import minidom

global http

http = httplib2.Http()

def bitrate():
    if xbmcplugin.getSetting("bitrate") == "0":
      return "mp4"
    elif xbmcplugin.getSetting("bitrate") == "1":
      return "flv"
    elif xbmcplugin.getSetting("bitrate") == "2":
      return "h264"
    elif xbmcplugin.getSetting("bitrate") == "3":
      return "ts"

#varmistetaan asetukset
def settings():
  if xbmcplugin.getSetting("username") != '' and xbmcplugin.getSetting("password") != '':
    menu()
  else:
    u=sys.argv[0]+"?url=Asetukset&mode=4"
    listfolder = xbmcgui.ListItem('-- Asetuksia ei maaritelty tai niissa on ongelma. Tarkista asetukset. --')
    listfolder.setInfo('video', {'Title': 'Asetuksia ei maaritelty tai niissa on ongelma. Tarkista asetukset.'})
    xbmcplugin.addDirectoryItem(int(sys.argv[1]), u, listfolder, isFolder=1)
    u=sys.argv[0]+"?url=Asetukset&mode=4"
    listfolder = xbmcgui.ListItem('Asetukset')
    listfolder.setInfo('video', {'Title': 'Asetukset'})
    xbmcplugin.addDirectoryItem(int(sys.argv[1]), u, listfolder, isFolder=1)

# paavalikko
def menu():
  u=sys.argv[0]+"?url="+urllib.quote_plus('http://alpha.tvkaista.fi/feed/channels/')+"&mode=1"
  listfolder = xbmcgui.ListItem('Kanavat')
  listfolder.setInfo('video', {'Title': "Kanavat"})
  xbmcplugin.addDirectoryItem(int(sys.argv[1]), u, listfolder, isFolder=1)

  u=sys.argv[0]+"?url="+urllib.quote_plus('http://alpha.tvkaista.fi/feed/seasonpasses/')+"&mode=1"
  listfolder = xbmcgui.ListItem('Sarjat')
  listfolder.setInfo('video', {'Title': "Sarjat"})
  xbmcplugin.addDirectoryItem(int(sys.argv[1]), u, listfolder, isFolder=1)

  u=sys.argv[0]+"?url="+urllib.quote_plus('http://alpha.tvkaista.fi/feed/playlist')+"&mode=2"
  listfolder = xbmcgui.ListItem('Lista')
  listfolder.setInfo('video', {'Title': 'Lista'})
  xbmcplugin.addDirectoryItem(int(sys.argv[1]), u, listfolder, isFolder=1)

  u=sys.argv[0]+"?url="+urllib.quote_plus('http://alpha.tvkaista.fi/feed/storage')+"&mode=2"
  listfolder = xbmcgui.ListItem('Varasto')
  listfolder.setInfo('video', {'Title': 'Varasto'})
  xbmcplugin.addDirectoryItem(int(sys.argv[1]), u, listfolder, isFolder=1)

  #TODO: asetuksiin mahdollisuus laittaa muitakin hakuja suoraan valikkoon
  u=sys.argv[0]+"?url="+urllib.quote_plus('http://alpha.tvkaista.fi/feed/search/title/elokuva')+"&mode=2"
  listfolder = xbmcgui.ListItem('Haku: elokuva')
  listfolder.setInfo('video', {'Title': 'Haku: elokuva'})
  xbmcplugin.addDirectoryItem(int(sys.argv[1]), u, listfolder, isFolder=1)

  u=sys.argv[0]+"?url=Haku&mode=3"
  listfolder = xbmcgui.ListItem('Haku')
  listfolder.setInfo('video', {'Title': 'Haku'})
  xbmcplugin.addDirectoryItem(int(sys.argv[1]), u, listfolder, isFolder=1)

  u=sys.argv[0]+"?url=Asetukset&mode=4"
  listfolder = xbmcgui.ListItem('Asetukset')
  listfolder.setInfo('video', {'Title': 'Asetukset'})
  xbmcplugin.addDirectoryItem(int(sys.argv[1]), u, listfolder, isFolder=1)

# Parsee kaynnistysparametrit kun skriptaa suoritetaan uudelleen
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

#Listaa feedin sisaltamat ohjelmat
#TODO: mediarss-feed, thumbnail (pitaa katsoa onko niiden lataaminen liian hidasta, asetus?)
#TODO: paivamaaravalikko "edellinen vuorokausi" sijaan
def listprograms(url):
  passman = urllib2.HTTPPasswordMgrWithDefaultRealm()
  passman.add_password(None, "http://alpha.tvkaista.fi", xbmcplugin.getSetting("username"), \
                         xbmcplugin.getSetting("password"))
  opener = urllib2.build_opener(urllib2.HTTPBasicAuthHandler(passman))
  urllib2.install_opener(opener)
  #print "listprograms avataan: "+url+'/'+bitrate()+'.rss'
  try:
      content = urllib2.urlopen(url+'/'+bitrate()+'.rss').read()
  except urllib2.HTTPError,e:
    u=sys.argv[0]
    listfolder = xbmcgui.ListItem('www-pyynto ei onnistunut '+str(e.code))
    listfolder.setInfo('video', {'Title': 'www-pyynto ei onnistunut '+str(e.code)})
    xbmcplugin.addDirectoryItem(int(sys.argv[1]), u, listfolder, isFolder=1)
    return
  dom = minidom.parseString(content)
  try:
    links = dom.getElementsByTagName('atom:link')
    #print "listprogram got links"
    for i in links:
      #print "link: "+i.attributes['rel'].value
      if i.attributes['rel'].value == "prev-archive":
        #print "href: "+i.attributes['href'].value
        newurl = re.compile(r"^(.*)/[^/]+[.]rss$", re.IGNORECASE).findall(i.attributes['href'].value)
        #print "newurl: "+newurl[0]
        u=sys.argv[0]+"?url="+urllib.quote_plus(newurl[0])+"&mode="+"2"
        listfolder = xbmcgui.ListItem('Edellinen vuorokausi')
        listfolder.setInfo('video', {'Title': 'Edellinen vuorokausi'})
        xbmcplugin.addDirectoryItem(int(sys.argv[1]), u, listfolder, isFolder=1)
  except:
    pass
  try:
    #haetaan aikaero GMT->lokaaliaika. Oletetaan, etta xbmc:n/pythonin aika on oikea lokaaliaika...
    otherdate=dom.getElementsByTagName('channel')[0].getElementsByTagName('lastBuildDate')[0].childNodes[0].nodeValue
    timediff=time.time()-time.mktime(time.strptime(otherdate,"%a, %d %b %Y %H:%M:%S +0000"))
  except:
    timediff=0

#  try:
  items = dom.getElementsByTagName('item')
  ret = []
  for i in items:
    ptit=i.getElementsByTagName('title')[0].childNodes[0].nodeValue
#    print "in "+ptit.encode("utf-8")
    try:
      pdes=i.getElementsByTagName('description')[0].childNodes[0].nodeValue
    except:
      pdes=""
    pdat=i.getElementsByTagName('pubDate')[0].childNodes[0].nodeValue
    pcha=i.getElementsByTagName('source')[0].childNodes[0].nodeValue
    try:
      purl=i.getElementsByTagName('enclosure')[0].attributes['url'].value
      pat = re.compile(r"http://alpha[.]tvkaista[.]fi/(.*)", re.IGNORECASE).findall(purl)
    except:
      pat=[]
      pat.append("")
      ptit=ptit+" -TALLENNE PUUTTUU-"
    if len(pdes)>80:
      shortdes=pdes[:80]+'...'
    else:
      shortdes=pdes
    t=time.localtime(timediff+time.mktime(time.strptime(pdat,"%a, %d %b %Y %H:%M:%S +0000")))
    urlii = 'http://%s:%s@alpha.tvkaista.fi/%s' % (\
            urllib.quote(xbmcplugin.getSetting("username")), \
            urllib.quote(xbmcplugin.getSetting("password")), pat[0])
    nimike = '%s | %s >>> %s (%s)' % (time.strftime("%H:%M",t),ptit,shortdes,pcha)

    listitem = xbmcgui.ListItem(label=nimike, iconImage="DefaultVideo.png")
    listitem.setInfo('video', {'title': nimike, 'plot': pdes, 
                               'date': time.strftime("%d.%m.%Y",t), })
    xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=urlii,listitem=listitem)
  xbmcplugin.addSortMethod(int(sys.argv[1]), xbmcplugin.SORT_METHOD_DATE)
#  except:
#    u=sys.argv[0]
#    listfolder = xbmcgui.ListItem('www-pyynnon sisallon tulkitseminen ei onnistunut')
#    listfolder.setInfo('video', {'Title': 'www-pyynnon sisallon tulkitseminen ei onnistunut'})
#    xbmcplugin.addDirectoryItem(int(sys.argv[1]), u, listfolder, isFolder=1)
  dom.unlink()

# Listaa feedin sisaltamat feedit
def listfeeds(url):
  passman = urllib2.HTTPPasswordMgrWithDefaultRealm()
  passman.add_password(None, "http://alpha.tvkaista.fi", xbmcplugin.getSetting("username"), \
                         xbmcplugin.getSetting("password"))
  opener = urllib2.build_opener(urllib2.HTTPBasicAuthHandler(passman))
  urllib2.install_opener(opener)
  #print "listfeeds avataan: "+url
  try:
      content = urllib2.urlopen(url).read()
  except urllib2.HTTPError,e:
    u=sys.argv[0]
    listfolder = xbmcgui.ListItem('www-pyynto ei onnistunut '+str(e.code))
    listfolder.setInfo('video', {'Title': 'www-pyynto ei onnistunut '+str(e.code)})
    xbmcplugin.addDirectoryItem(int(sys.argv[1]), u, listfolder, isFolder=1)
    return
#  try:
  dom = minidom.parseString(content)
  items = dom.getElementsByTagName('item')
  ret = []
  for i in items:
    ptit=i.getElementsByTagName('title')[0].childNodes[0].nodeValue
    plin=i.getElementsByTagName('link')[0].childNodes[0].nodeValue
    u=sys.argv[0]+"?url="+urllib.quote_plus(plin)+"&mode="+"2"
    listfolder = xbmcgui.ListItem(ptit)
    listfolder.setInfo('video', {'Title': ptit})
    xbmcplugin.addDirectoryItem(int(sys.argv[1]), u, listfolder, isFolder=1)
#  except:
#    u=sys.argv[0]
#    listfolder = xbmcgui.ListItem('www-pyynnon sisallon tulkitseminen ei onnistunut')
#    listfolder.setInfo('video', {'Title': 'www-pyynnon sisallon tulkitseminen ei onnistunut'})
#    xbmcplugin.addDirectoryItem(int(sys.argv[1]), u, listfolder, isFolder=1)
  dom.unlink()

# Antaa kayttajalle virtuaalisen nappaimiston ja listaa hakutulokset
def search():
  keyboard = xbmc.Keyboard()
  keyboard.doModal()
  if (keyboard.isConfirmed()):
    url = 'http://alpha.tvkaista.fi/feed/search/title/%s' % (urllib.quote_plus(keyboard.getText()))
    listprograms(url)

params=get_params()
url=None
mode=None
try:
        url=urllib.unquote_plus(params["url"])
except:
        pass
try:
        mode=int(params["mode"])
except:
        pass

if mode==None or url==None or len(url)<1:
        settings()
        
elif mode==1:
        listfeeds(url)
elif mode==2:
        listprograms(url)
elif mode==3:
        search()
elif mode==4:
        xbmcplugin.openSettings(url=sys.argv[0])

# Kaikki kunnossa, ilmoitetaan etta tassa oli kaikki
xbmcplugin.endOfDirectory(int(sys.argv[1]))
