get_Schedule <- function(output_file = "OHL_Schedule_2024_2025.csv") {
  # Load required libraries
  library(tidyverse)
  library(jsonlite)

  # Define the URL with the updated season_id
  url_schedule <- "https://lscluster.hockeytech.com/feed/?feed=modulekit&view=scorebar&client_code=ohl&numberofdaysahead=100&numberofdaysback=90&season_id=79&team_id=&key=f1aa699db3d81487"

  # Fetch JSON data from the URL
  json_data_schedule <- fromJSON(url_schedule, simplifyDataFrame = TRUE)

  # Debug: Print the structure of the JSON data
  print("JSON structure:")
  str(json_data_schedule)

  # Extract the games data from the JSON
  if (!is.null(json_data_schedule[["SiteKit"]][["Scorebar"]])) {
    games_data <- json_data_schedule[["SiteKit"]][["Scorebar"]]
  } else {
    stop("Could not extract games data from the JSON.")
  }

  # Convert the games data to a tibble and select relevant columns
  Schedule <- as_tibble(games_data) %>%
    select(
      Date = Date,
      Time = ScheduledFormattedTime,
      HomeTeam = HomeLongName,
      HomeGoals = HomeGoals,
      AwayTeam = VisitorLongName,
      AwayGoals = VisitorGoals,
      GameID = ID
    )

  # Save the schedule as a CSV file
  write_csv(Schedule, output_file)

  # Return the schedule as a data frame
  return(Schedule)
}

# Run the function and save the schedule
tryCatch(
  {
    schedule <- get_Schedule("OHL_Schedule_2024_2025.csv")
    print("Schedule saved successfully:")
    print(head(schedule))
  },
  error = function(e) {
    print(paste("Error:", e$message))
  }
)
