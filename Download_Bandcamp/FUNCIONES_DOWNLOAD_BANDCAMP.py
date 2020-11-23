#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jun 29 13:49:29 2019

@author: oscar
"""

from bs4 import BeautifulSoup
import requests
import numpy as np
import os
import re
import tqdm
import multiprocessing as mp
from  itertools import chain
from mutagen import File        
from mutagen.id3 import TPE1, TIT2, TALB, APIC
from functools import partial

'''
###############################################################################
###############################################################################
TODO... FUNCION DESCARGAR CANCION, DESCARGAR ALBUM Y DESCARGAR CANAL.
PARA PODER HACERLO EN PARALELO
###############################################################################
###############################################################################
'''


    
def LOOK_FOR_TRACKS_AND_ALBUMS_IN_URL(url):
    
    session = requests.Session()
    session.trust_env = False
    user_agents= session.get(url)
    BS4_ELEMENT = BeautifulSoup(user_agents.content, 'html.parser')
    '''
    INTROUDCIMOS UN ELEMENTO BS4 Y DEVUELVE 
    LOS LINKS DE ALBUMES Y LAS CANCIONES
    '''
    try:
        BS4_ELEMENT.find('div',  {'class':'recommendations-container'}).decompose()
    except:
        pass

    LINKS_BS4= []
    for a in BS4_ELEMENT.find_all(href=True):
        LINKS_BS4.append(a['href'])
    
    URL_CANAL= url.replace('https://', '').split('/')[0]
    URL_CANAL= 'https://' + URL_CANAL
    ALBUMS= [link if 'https://' in link else URL_CANAL + link for link in LINKS_BS4 if '/album/' in link]
    ALBUMS= list(dict.fromkeys(ALBUMS))
    
    
    SONGS= [link if 'https://' in link else URL_CANAL + link for link in LINKS_BS4 if '/track/' in link]
    SONGS= [item for item in SONGS if '?action=download' not in item]
    SONGS= list(dict.fromkeys(SONGS))
    
    try:
        PATRON_STREAM = re.compile('https://t4.bcbits.com/stream/'   
                                '[^\"]+' )                        
        AUDIO_URL=re.findall(PATRON_STREAM,user_agents.text)[0]
    except: 
        AUDIO_URL= []
   
    try:
        PATRON_IMG = re.compile('<img src="(https://f4.bcbits.com/img/.[^\.]+.jpg)')
                                     
        IMG_URL=re.findall(PATRON_IMG,user_agents.text)[0]
    except: 
        IMG_URL= []
        
    return {'ALBUMS': ALBUMS, 'TRACKS': SONGS, 'AUDIO':AUDIO_URL, 'IMG':IMG_URL}


def DOWNLOAD_TRACK_BANDCAMP(TRACKS, PATH_DONWLOAD):
    try:
        session = requests.Session()
        session.trust_env = False
        user_agents= session.get(TRACKS)
            
        #PARSEANDO HTML
        user_soup = BeautifulSoup(user_agents.content, 'html.parser')
        NAME_SECTION= [item for item in user_soup.find_all('div', { "id" : "name-section" })][0]
               
        try: 
          SONG_NAME= NAME_SECTION.find('', {'class':'trackTitle'}).text.replace('\n','').strip()
        except:
          SONG_NAME= TRACKS.split('track/')[1]
          
        try:
          ARTIST_NAME= NAME_SECTION.find('', {'itemprop':'byArtist'}).text.replace('\n','').strip()
          HREF_ARTIST= [item['href'] for item in NAME_SECTION.find('', {'itemprop':'byArtist'}).find_all(href= True)]
          INFO_ARTISTA= '--------'.join(list(chain(*[[ARTIST_NAME], HREF_ARTIST])))
        except:
          ARTIST_NAME=''
      
        
        IMG_AUDIO= LOOK_FOR_TRACKS_AND_ALBUMS_IN_URL(TRACKS)
        HREF_AUDIO= IMG_AUDIO['AUDIO']
        HREF_IMG= IMG_AUDIO['IMG']
        
        
        
        if not os.path.exists(PATH_DONWLOAD):
            os.makedirs(PATH_DONWLOAD, exist_ok=True)
        
        
    
        IMG = requests.get(HREF_IMG, allow_redirects=True)
        open(os.path.join(PATH_DONWLOAD, 'cover.jpg'), 'wb').write(IMG.content)  #Karatula jaitsi
    
        SONG_FILE= os.path.join(PATH_DONWLOAD, SONG_NAME + '.mp3')
    
        if not os.path.exists(SONG_FILE):
            SONG = requests.get(HREF_AUDIO, allow_redirects=True)
            
            open(SONG_FILE, 'wb').write(SONG.content)        #Fitxategiari izen generikoa jarriko diogu amaierako izenaren ordez komando hau karaktere batzuekin moskeatu egiten delako
    
           #Metadatuak gehitu
            audio=File(SONG_FILE)
            audio['TPE1'] = TPE1(encoding=3, text=ARTIST_NAME)
            audio['TIT2'] = TIT2(encoding=3, text=SONG_NAME)
           #audio['TRCK'] = TRCK(encoding=3, text=zenbakia)
            audio['TALB'] = TALB(encoding=3, text=os.path.split(PATH_DONWLOAD)[1])
           #Karatula jarri
            with open(os.path.join(PATH_DONWLOAD, 'cover.jpg'), 'rb') as albumart:
                  audio['APIC'] = APIC(
                                encoding=3,
                                mime='image/jpeg',
                                type=3, desc=u'Cover',
                                data=albumart.read()
                                )       
            audio.save()
        else:
            print(SONG_NAME + ' YA HA SIDO DESCARGADA')
        
        
        
        return(TRACKS + '__DOWNLOADED')
    except:
        return(TRACKS + '__ERROR')



def DOWNLOAD_ALBUM(ALBUMS, CHANNEL_NAME, BANDCAMP_PATH):
    
          session = requests.Session()
          session.trust_env = False
          user_agents= session.get(ALBUMS)
          
          #PARSEANDO HTML
          user_soup = BeautifulSoup(user_agents.content, 'html.parser')
              
          NAME_SECTION= [item for item in user_soup.find_all('div', { "id" : "name-section" })][0]
          try: 
              ALBUMA_NAME= NAME_SECTION.find('', {'class':'trackTitle'}).text.replace('\n','').strip()
          except:
              ALBUMA_NAME= ALBUMS.split('album/')[1]
              
          try:
              ARTIST_NAME= NAME_SECTION.find('', {'itemprop':'byArtist'}).text.replace('\n','').strip()
              HREF_ARTIST= [item['href'] for item in NAME_SECTION.find('', {'itemprop':'byArtist'}).find_all(href= True)]
              INFO_ARTISTA= '--------'.join(list(chain(*[[ARTIST_NAME], HREF_ARTIST])))
          except:
              ARTIST_NAME=''
          
          
               
               
          
          TRACKS_IN_ALBUM= LOOK_FOR_TRACKS_AND_ALBUMS_IN_URL(ALBUMS)['TRACKS']
          PATH_DOWNLOAD= os.path.join(BANDCAMP_PATH, CHANNEL_NAME, ALBUMA_NAME)
          
          exe=True
          
          if os.path.exists(PATH_DOWNLOAD): 
              if len([item for item in os.listdir(PATH_DOWNLOAD) if '.mp3' in item])==len(TRACKS_IN_ALBUM):
                  print('ALBUM YA DESCARGADO')
                  exe=False
          
          if len(TRACKS_IN_ALBUM)==0:
                  print('EMPTY')
                  exe=False

          if exe:
              if True: 
                func = partial(DOWNLOAD_TRACK_BANDCAMP, PATH_DONWLOAD= PATH_DOWNLOAD)
                pool = mp.Pool(len(TRACKS_IN_ALBUM) if len(TRACKS_IN_ALBUM)<8 else 8)
                results=[]
                for _ in tqdm.tqdm(pool.imap_unordered(func, TRACKS_IN_ALBUM), total=len(TRACKS_IN_ALBUM)):
                    results.append(_)
                    pass
                #MATAMOS SUBPROCESOS 
                pool.close()
                pool.terminate()
                pool.join()
              else:
                for TRACK in TRACKS_IN_ALBUM:
                      DOWNLOAD_TRACK_BANDCAMP(TRACK, PATH_DONWLOAD=  os.path.join(BANDCAMP_PATH, CHANNEL_NAME, ALBUMA_NAME))
    
            

    



def DOWNLOAD_ENTIRE_LABEL(CHANNEL, BANDCAMP_PATH):
        
        BANDCAMP_PATH= BANDCAMP_PATH
      
        session = requests.Session()
        session.trust_env = False
        user_agents= session.get(CHANNEL)
            
        user_soup = BeautifulSoup(user_agents.content, 'html.parser')
        CHANNEL_NAME= user_soup.find('head').find('title').text.replace('\n','').strip()
        
    
            
        
        HREFS= LOOK_FOR_TRACKS_AND_ALBUMS_IN_URL(CHANNEL)
    
        
        
        for ALBUMS in HREFS['ALBUMS']:
            DOWNLOAD_ALBUM(ALBUMS, CHANNEL_NAME, BANDCAMP_PATH)
         

