library(shiny)
library(DT)


ui <- fluidPage(
    tabsetPanel(id='tabpan', type= 'tabs',
                tabPanel(title = 'Download Center', id= 'down',
                         actionButton("down_btn", "Download Labels")
                         
                         ),
                
                tabPanel(title = 'Modify Registry',id= 'registry',
                         sidebarLayout(
                             sidebarPanel(
                                 actionButton("add_btn", "Add"),
                                 actionButton("delete_btn", "Delete"),
                                 actionButton("save_btn", "Save"),
                                 #tags$audio(src = 'AWB - Loose Fit.mp3', type = "audio/mp3", autoplay = NA, controls = NA)
                                 
                                 
                             ),
                             
                             mainPanel(
                                 DTOutput("shiny_table")
                             )
                         )
                         )
                
                )
    
   
)

server <- function(input, output) {
    
    df<- readRDS(here::here('URLS_CHANNELS.RDS'))
    this_table<- reactiveVal(df)
    
    observeEvent(input$add_btn, {
        t = rbind(data.frame(NAME= '',URL= '', stringsAsFactors = FALSE), this_table())
        this_table(t)
    })
    
    
    
    observeEvent(input[["shiny_table_cell_edit"]], {
        cell <- input[["shiny_table_cell_edit"]]
        newdf <- this_table()
        newdf[cell$row, cell$col] <- cell$value %>% as.character()
        this_table(newdf)
    })

    
    observeEvent(input$delete_btn, {
        t = this_table()
        print(nrow(t))
        if (!is.null(input$shiny_table_rows_selected)) {
            t <- t[-as.numeric(input$shiny_table_rows_selected),]
        }
        this_table(t)
    })
    observeEvent(input$save_btn, {
       this_table() %>% saveRDS(here::here('URLS_CHANNELS.RDS'))
    })
    
    output$shiny_table <- renderDT({
        datatable(this_table() %>% data.frame(row.names = NULL), 
                  selection = 'single', 
                  options = list(dom = 't'),
                  editable = "cell")
    })
    
    observeEvent(input$down_btn, {
       source('DOWNLOAD_LABELS_IN_REGISTRY.R')
    })
 
}

shinyApp(ui = ui, server = server)
