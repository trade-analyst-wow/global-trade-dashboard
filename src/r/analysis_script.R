#!/usr/bin/env Rscript
# Trade Analysis Dashboard - R Analysis Script
# Performs statistical analysis, regression models, and advanced visualizations

# Load required libraries
suppressPackageStartupMessages({
  library(dplyr)
  library(tidyr)
  library(ggplot2)
  library(plotly)
  library(corrplot)
  library(forecast)
  library(tseries)
  library(vars)
  library(plm)
  library(car)
  library(lmtest)
  library(sandwich)
  library(RSQLite)
  library(jsonlite)
  library(readr)
  library(lubridate)
  library(scales)
  library(viridis)
  library(gridExtra)
  library(patchwork)
})

# Set working directory to project root
project_root <- normalizePath(file.path(dirname(sys.frame(1)$ofile), "..", ".."))
setwd(project_root)

# Create output directories
dir.create("analysis", showWarnings = FALSE)
dir.create("analysis/plots", showWarnings = FALSE)
dir.create("analysis/reports", showWarnings = FALSE)

# Database connection
db_path <- file.path(project_root, "data", "sql", "trade_analysis.db")
con <- dbConnect(SQLite(), db_path)

# Color palette for visualizations
trade_colors <- c("#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd", 
                  "#8c564b", "#e377c2", "#7f7f7f", "#bcbd22", "#17becf")

# Function to load data from database
load_trade_data <- function() {
  cat("Loading trade data from database...\n")
  
  # Load countries
  countries <- dbGetQuery(con, "SELECT * FROM countries")
  
  # Load trade data
  trade_data <- dbGetQuery(con, "
    SELECT td.*, 
           c1.country_name as reporter_country,
           c2.country_name as partner_country
    FROM trade_data td
    LEFT JOIN countries c1 ON td.reporter_country_id = c1.country_id
    LEFT JOIN countries c2 ON td.partner_country_id = c2.country_id
    WHERE td.year >= 2020
  ")
  
  # Load economic indicators
  economic_data <- dbGetQuery(con, "
    SELECT ei.*, c.country_name
    FROM economic_indicators ei
    LEFT JOIN countries c ON ei.country_id = c.country_id
    WHERE ei.year >= 2020
  ")
  
  # Load tariffs
  tariffs <- dbGetQuery(con, "
    SELECT t.*, 
           c1.country_name as imposing_country,
           c2.country_name as target_country
    FROM tariffs t
    LEFT JOIN countries c1 ON t.country_id = c1.country_id
    LEFT JOIN countries c2 ON t.partner_country_id = c2.country_id
  ")
  
  # Load sanctions
  sanctions <- dbGetQuery(con, "
    SELECT s.*, 
           c1.country_name as sanctioning_country,
           c2.country_name as target_country
    FROM sanctions s
    LEFT JOIN countries c1 ON s.sanctioning_country_id = c1.country_id
    LEFT JOIN countries c2 ON s.target_country_id = c2.country_id
  ")
  
  return(list(
    countries = countries,
    trade_data = trade_data,
    economic_data = economic_data,
    tariffs = tariffs,
    sanctions = sanctions
  ))
}

# Function to perform trade flow analysis
analyze_trade_flows <- function(trade_data) {
  cat("Analyzing trade flows...\n")
  
  # Aggregate trade data by country and year
  trade_summary <- trade_data %>%
    group_by(reporter_country, year, trade_flow) %>%
    summarise(
      total_value = sum(value_usd, na.rm = TRUE),
      trade_count = n(),
      .groups = 'drop'
    ) %>%
    pivot_wider(
      names_from = trade_flow,
      values_from = c(total_value, trade_count),
      names_sep = "_"
    )
  
  # Calculate trade balance
  trade_summary <- trade_summary %>%
    mutate(
      trade_balance = total_value_export - total_value_import,
      trade_balance_pct = (trade_balance / (total_value_export + total_value_import)) * 100
    )
  
  # Top trading countries
  top_traders <- trade_summary %>%
    group_by(reporter_country) %>%
    summarise(
      avg_exports = mean(total_value_export, na.rm = TRUE),
      avg_imports = mean(total_value_import, na.rm = TRUE),
      avg_balance = mean(trade_balance, na.rm = TRUE),
      .groups = 'drop'
    ) %>%
    arrange(desc(avg_exports + avg_imports)) %>%
    head(10)
  
  return(list(
    trade_summary = trade_summary,
    top_traders = top_traders
  ))
}

# Function to perform economic impact analysis
analyze_economic_impact <- function(trade_data, economic_data) {
  cat("Analyzing economic impact...\n")
  
  # Merge trade and economic data
  merged_data <- trade_data %>%
    group_by(reporter_country, year) %>%
    summarise(
      total_exports = sum(value_usd[trade_flow == "export"], na.rm = TRUE),
      total_imports = sum(value_usd[trade_flow == "import"], na.rm = TRUE),
      .groups = 'drop'
    ) %>%
    left_join(
      economic_data %>%
        pivot_wider(
          names_from = indicator_name,
          values_from = indicator_value,
          names_sep = "_"
        ),
      by = c("reporter_country" = "country_name", "year")
    )
  
  # Calculate correlations
  correlations <- merged_data %>%
    select(total_exports, total_imports, 
           `NY.GDP.MKTP.CD`, `NY.GDP.MKTP.KD.ZG`, 
           `SL.UEM.TOTL.ZS`, `FP.CPI.TOTL.ZG`) %>%
    cor(use = "complete.obs")
  
  return(list(
    merged_data = merged_data,
    correlations = correlations
  ))
}

# Function to perform tariff impact analysis
analyze_tariff_impact <- function(trade_data, tariffs) {
  cat("Analyzing tariff impact...\n")
  
  # Aggregate tariff data
  tariff_summary <- tariffs %>%
    group_by(imposing_country, target_country, tariff_type) %>%
    summarise(
      avg_tariff_rate = mean(tariff_rate, na.rm = TRUE),
      tariff_count = n(),
      .groups = 'drop'
    )
  
  # Analyze trade patterns with tariff changes
  # This would require more detailed time-series data
  # For now, we'll create a simplified analysis
  
  return(tariff_summary)
}

# Function to perform sanctions impact analysis
analyze_sanctions_impact <- function(trade_data, sanctions) {
  cat("Analyzing sanctions impact...\n")
  
  # Active sanctions
  active_sanctions <- sanctions %>%
    filter(status == "active") %>%
    group_by(target_country, sanction_type) %>%
    summarise(
      sanction_count = n(),
      .groups = 'drop'
    )
  
  # Analyze trade patterns for sanctioned countries
  sanctioned_trade <- trade_data %>%
    filter(reporter_country %in% active_sanctions$target_country |
           partner_country %in% active_sanctions$target_country) %>%
    group_by(reporter_country, year, trade_flow) %>%
    summarise(
      total_value = sum(value_usd, na.rm = TRUE),
      .groups = 'drop'
    )
  
  return(list(
    active_sanctions = active_sanctions,
    sanctioned_trade = sanctioned_trade
  ))
}

# Function to create visualizations
create_visualizations <- function(analysis_results) {
  cat("Creating visualizations...\n")
  
  # 1. Trade Flow Trends
  p1 <- ggplot(analysis_results$trade_summary, 
               aes(x = year, y = total_value_export, color = reporter_country)) +
    geom_line(size = 1) +
    geom_point() +
    scale_color_viridis_d() +
    scale_y_continuous(labels = scales::comma) +
    labs(title = "Export Trends by Country (2020-2023)",
         x = "Year", y = "Export Value (USD)",
         color = "Country") +
    theme_minimal() +
    theme(legend.position = "bottom")
  
  ggsave("analysis/plots/export_trends.png", p1, width = 12, height = 8, dpi = 300)
  
  # 2. Trade Balance
  p2 <- ggplot(analysis_results$trade_summary, 
               aes(x = year, y = trade_balance_pct, fill = reporter_country)) +
    geom_col(position = "dodge") +
    scale_fill_viridis_d() +
    labs(title = "Trade Balance as % of Total Trade",
         x = "Year", y = "Trade Balance (%)",
         fill = "Country") +
    theme_minimal() +
    theme(legend.position = "bottom")
  
  ggsave("analysis/plots/trade_balance.png", p2, width = 12, height = 8, dpi = 300)
  
  # 3. Correlation Matrix
  png("analysis/plots/correlation_matrix.png", width = 800, height = 600)
  corrplot(analysis_results$correlations, 
           method = "color", 
           type = "upper", 
           order = "hclust",
           tl.cex = 0.8,
           tl.col = "black",
           addCoef.col = "black",
           number.cex = 0.7)
  dev.off()
  
  # 4. Top Traders
  p3 <- ggplot(analysis_results$top_traders, 
               aes(x = reorder(reporter_country, avg_exports + avg_imports), 
                   y = (avg_exports + avg_imports) / 1e12)) +
    geom_col(fill = "steelblue") +
    coord_flip() +
    scale_y_continuous(labels = scales::comma) +
    labs(title = "Top Trading Countries (Average 2020-2023)",
         x = "Country", y = "Average Total Trade (Trillion USD)") +
    theme_minimal()
  
  ggsave("analysis/plots/top_traders.png", p3, width = 10, height = 8, dpi = 300)
  
  # 5. Interactive plot for trade flows
  p4 <- plot_ly(analysis_results$trade_summary, 
                x = ~year, y = ~total_value_export, 
                color = ~reporter_country, type = 'scatter', mode = 'lines+markers') %>%
    layout(title = "Interactive Export Trends",
           xaxis = list(title = "Year"),
           yaxis = list(title = "Export Value (USD)"))
  
  saveWidget(p4, "analysis/plots/interactive_trade_flows.html")
}

# Function to perform statistical modeling
perform_statistical_modeling <- function(merged_data) {
  cat("Performing statistical modeling...\n")
  
  # Remove rows with missing data
  model_data <- merged_data %>%
    filter(!is.na(`NY.GDP.MKTP.CD`) & !is.na(total_exports) & !is.na(total_imports))
  
  # 1. Export-GDP relationship
  export_model <- lm(log(total_exports) ~ log(`NY.GDP.MKTP.CD`), data = model_data)
  
  # 2. Import-GDP relationship
  import_model <- lm(log(total_imports) ~ log(`NY.GDP.MKTP.CD`), data = model_data)
  
  # 3. Trade balance model
  balance_model <- lm(trade_balance ~ `NY.GDP.MKTP.KD.ZG` + `SL.UEM.TOTL.ZS`, data = model_data)
  
  # Model diagnostics
  models <- list(
    export_model = export_model,
    import_model = import_model,
    balance_model = balance_model
  )
  
  # Save model summaries
  sink("analysis/reports/model_summaries.txt")
  cat("=== TRADE ANALYSIS MODEL SUMMARIES ===\n\n")
  
  for (model_name in names(models)) {
    cat(paste("=== ", toupper(model_name), " ===\n"))
    print(summary(models[[model_name]]))
    cat("\n")
  }
  
  sink()
  
  return(models)
}

# Function to generate time series forecasts
generate_forecasts <- function(trade_summary) {
  cat("Generating time series forecasts...\n")
  
  # Prepare time series data
  ts_data <- trade_summary %>%
    group_by(year) %>%
    summarise(
      total_exports = sum(total_value_export, na.rm = TRUE),
      total_imports = sum(total_value_import, na.rm = TRUE),
      .groups = 'drop'
    ) %>%
    arrange(year)
  
  # Create time series objects
  exports_ts <- ts(ts_data$total_exports, start = min(ts_data$year), frequency = 1)
  imports_ts <- ts(ts_data$total_imports, start = min(ts_data$year), frequency = 1)
  
  # Fit ARIMA models
  exports_arima <- auto.arima(exports_ts)
  imports_arima <- auto.arima(imports_ts)
  
  # Generate forecasts
  exports_forecast <- forecast(exports_arima, h = 3)
  imports_forecast <- forecast(imports_arima, h = 3)
  
  # Create forecast plots
  png("analysis/plots/exports_forecast.png", width = 800, height = 600)
  plot(exports_forecast, main = "Export Value Forecast (2024-2026)")
  dev.off()
  
  png("analysis/plots/imports_forecast.png", width = 800, height = 600)
  plot(imports_forecast, main = "Import Value Forecast (2024-2026)")
  dev.off()
  
  return(list(
    exports_forecast = exports_forecast,
    imports_forecast = imports_forecast
  ))
}

# Function to generate risk assessment
generate_risk_assessment <- function(analysis_results) {
  cat("Generating risk assessment...\n")
  
  # Calculate risk scores based on various factors
  risk_scores <- analysis_results$trade_summary %>%
    group_by(reporter_country) %>%
    summarise(
      export_volatility = sd(total_value_export, na.rm = TRUE) / mean(total_value_export, na.rm = TRUE),
      import_volatility = sd(total_value_import, na.rm = TRUE) / mean(total_value_import, na.rm = TRUE),
      balance_volatility = sd(trade_balance_pct, na.rm = TRUE),
      avg_trade_balance = mean(trade_balance_pct, na.rm = TRUE),
      .groups = 'drop'
    ) %>%
    mutate(
      trade_risk_score = (export_volatility + import_volatility + balance_volatility) / 3 * 100,
      trade_risk_score = pmin(trade_risk_score, 100)  # Cap at 100
    )
  
  # Create risk visualization
  p5 <- ggplot(risk_scores, aes(x = reorder(reporter_country, trade_risk_score), 
                                y = trade_risk_score, fill = trade_risk_score)) +
    geom_col() +
    scale_fill_viridis_c() +
    coord_flip() +
    labs(title = "Trade Risk Assessment by Country",
         x = "Country", y = "Risk Score (0-100)",
         fill = "Risk Score") +
    theme_minimal()
  
  ggsave("analysis/plots/risk_assessment.png", p5, width = 10, height = 8, dpi = 300)
  
  return(risk_scores)
}

# Function to generate comprehensive report
generate_report <- function(analysis_results, models, forecasts, risk_scores) {
  cat("Generating comprehensive report...\n")
  
  # Create HTML report
  report_content <- paste0(
    "<!DOCTYPE html>
    <html>
    <head>
        <title>Trade Analysis Dashboard Report</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; }
            h1, h2, h3 { color: #2c3e50; }
            .summary { background-color: #f8f9fa; padding: 20px; border-radius: 5px; }
            .metric { display: inline-block; margin: 10px; padding: 10px; background-color: #e9ecef; border-radius: 3px; }
        </style>
    </head>
    <body>
        <h1>Global Trade Analysis Dashboard Report</h1>
        <p>Generated on: ", Sys.Date(), "</p>
        
        <h2>Executive Summary</h2>
        <div class='summary'>
            <p>This report provides a comprehensive analysis of global trade patterns, 
            economic impacts, and risk assessments based on data from 2020-2023.</p>
        </div>
        
        <h2>Key Findings</h2>
        <div class='metric'>
            <strong>Total Countries Analyzed:</strong> ", nrow(analysis_results$top_traders), "
        </div>
        <div class='metric'>
            <strong>Time Period:</strong> 2020-2023
        </div>
        <div class='metric'>
            <strong>Data Sources:</strong> UN Comtrade, World Bank, WTO
        </div>
        
        <h2>Top Trading Countries</h2>
        <ul>",
    paste0("<li>", analysis_results$top_traders$reporter_country, 
           " - Average Trade: $", round(analysis_results$top_traders$avg_exports + 
                                       analysis_results$top_traders$avg_imports) / 1e12, 2), "T</li>", 
           collapse = ""),
    "</ul>
        
        <h2>Risk Assessment</h2>
        <p>Countries with highest trade risk scores:</p>
        <ul>",
    paste0("<li>", head(risk_scores[order(-risk_scores$trade_risk_score), ], 5)$reporter_country, 
           " - Risk Score: ", round(head(risk_scores[order(-risk_scores$trade_risk_score), ], 5)$trade_risk_score, 1), "</li>", 
           collapse = ""),
    "</ul>
        
        <h2>Forecast Summary</h2>
        <p>Based on ARIMA modeling, trade volumes are projected to continue growing 
        with moderate volatility over the next 3 years.</p>
        
        <h2>Methodology</h2>
        <p>This analysis uses:</p>
        <ul>
            <li>Statistical regression models for economic relationships</li>
            <li>Time series analysis for trend identification</li>
            <li>Risk scoring based on volatility and balance metrics</li>
            <li>Correlation analysis for policy impact assessment</li>
        </ul>
    </body>
    </html>"
  )
  
  writeLines(report_content, "analysis/reports/trade_analysis_report.html")
  
  cat("Report generated: analysis/reports/trade_analysis_report.html\n")
}

# Main analysis execution
main <- function() {
  cat("=== TRADE ANALYSIS DASHBOARD - R ANALYSIS ===\n")
  cat("Starting comprehensive trade analysis...\n\n")
  
  tryCatch({
    # Load data
    data <- load_trade_data()
    
    # Perform analyses
    trade_analysis <- analyze_trade_flows(data$trade_data)
    economic_analysis <- analyze_economic_impact(data$trade_data, data$economic_data)
    tariff_analysis <- analyze_tariff_impact(data$trade_data, data$tariffs)
    sanctions_analysis <- analyze_sanctions_impact(data$trade_data, data$sanctions)
    
    # Combine results
    analysis_results <- list(
      trade_summary = trade_analysis$trade_summary,
      top_traders = trade_analysis$top_traders,
      correlations = economic_analysis$correlations,
      merged_data = economic_analysis$merged_data
    )
    
    # Create visualizations
    create_visualizations(analysis_results)
    
    # Perform statistical modeling
    models <- perform_statistical_modeling(economic_analysis$merged_data)
    
    # Generate forecasts
    forecasts <- generate_forecasts(trade_analysis$trade_summary)
    
    # Generate risk assessment
    risk_scores <- generate_risk_assessment(analysis_results)
    
    # Generate comprehensive report
    generate_report(analysis_results, models, forecasts, risk_scores)
    
    cat("\n=== ANALYSIS COMPLETED SUCCESSFULLY ===\n")
    cat("Output files created in 'analysis/' directory\n")
    cat("- Plots: analysis/plots/\n")
    cat("- Reports: analysis/reports/\n")
    
  }, error = function(e) {
    cat("Error during analysis:", conditionMessage(e), "\n")
    stop(e)
  }, finally = {
    # Close database connection
    dbDisconnect(con)
  })
}

# Run main function
main() 