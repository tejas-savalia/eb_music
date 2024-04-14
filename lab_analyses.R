library(dplyr)
library(ggplot2)



clean_data <- function(filename) {
  tryCatch({
    data <- read.csv(paste0("data/", filename))
    
    # Drop instruction rows by dropping rows with missing data in column: 'blocks.thisRepN'
    data <- data[complete.cases(data$blocks.thisRepN), ]
    
    # If data file is incomplete, raise an error.
    if (sum(!is.na(data$node.idx)) < 1400) {
      stop("Incomplete Data")
    }
    
    # Rt is average rt of all keys pressed
    data$rt <- sapply(seq_len(nrow(data)), function(i) {
      mean(unlist(strsplit(as.character(data$key_resp.rt[i]), ","))) 
      ifelse(data$accuracy[i], NaN, NA)
    })
    
    # Transition type is cross cluster if goes from boundary to boundary
    data$transition_type <- ifelse(data$node.type == "boundary" & 
                                     data$node.type == lag(data$node.type, default = NA),
                                   "cross cluster", "within cluster")
    
    # Label conditions based on participant number as was designed in the experiment
    if (data$participant[1] %% 3 == 0) {
      data$condition <- "random"
    } else if (data$participant[1] %% 3 == 1) {
      data$condition <- "music random"
    } else {
      data$condition <- "structured"
    }
    
    data$trial <- seq_len(nrow(data))
    
  }, error = function(e) {
    return(NULL)
  })
  
  # Count the number of keys to be pressed for each stimuli
  data$num_keypress <- sapply(seq_len(nrow(data)), function(i) {
    length(unlist(strsplit(as.character(data$stim[i]), "")))
  })
  
  # Return the dataframe with relevant columns
  return(data[c("participant", "blocks.thisRepN", "accuracy", "condition", 
                "node.type",  "rt", "stim")])
}


# List of data files
data_files <- list.files('data/', pattern = '^240.*\\.csv$')

# Applying clean_data function to each file and combining into a single dataframe
df_clean <- lapply(data_files, clean_data) %>%
  bind_rows() %>%
  mutate(index = row_number()) %>%
  select(-index)


df_clean$node_transition_type <- paste(df_clean$node.type, 
                                                 df_clean$transition_type, 
                                                 sep = "_")


ggplot(df_clean, aes(x = factor(blocks.thisRepN), y = rt, color = node_transition_type)) +
  geom_point(position = position_dodge(width = 0.5)) +
  facet_grid(. ~ condition) +
  theme_minimal() +
  labs(x = "blocks.thisRepN", y = "rt") +
  theme(legend.position = "right") +
  scale_color_brewer(palette = "Set1")  
