library(reticulate)
source_python(here::here('Download_Bandcamp/FUNCIONES_DOWNLOAD_BANDCAMP.py'))

URL_LABEL<- readRDS(here::here('URLS_CHANNELS.RDS'))

for (url in URL_LABEL$URL) {
  DOWNLOAD_ENTIRE_LABEL(url, BANDCAMP_PATH=here::here('Download_Bandcamp/BANDCAMP/'))
}
  


