# R Package Requirements for Trade Analysis Dashboard
# Run this script to install all required packages

# Function to install packages if not already installed
install_if_missing <- function(packages) {
  for (package in packages) {
    if (!require(package, character.only = TRUE)) {
      install.packages(package, dependencies = TRUE)
      library(package, character.only = TRUE)
    }
  }
}

# Core Data Manipulation and Analysis
core_packages <- c(
  "dplyr",           # Data manipulation
  "tidyr",           # Data tidying
  "readr",           # Fast data reading
  "readxl",          # Excel file reading
  "writexl",         # Excel file writing
  "data.table",      # Fast data operations
  "stringr",         # String manipulation
  "lubridate",       # Date/time manipulation
  "forcats"          # Factor manipulation
)

# Statistical Analysis
stats_packages <- c(
  "stats",           # Base statistics
  "MASS",            # Modern Applied Statistics
  "car",             # Companion to Applied Regression
  "lmtest",          # Linear Model Tests
  "sandwich",        # Robust Covariance Matrix Estimators
  "plm",             # Panel Data Econometrics
  "AER",             # Applied Econometrics with R
  "forecast",        # Time Series Forecasting
  "tseries",         # Time Series Analysis
  "vars",            # Vector Autoregressive Models
  "urca",            # Unit Root and Cointegration Tests
  "strucchange",     # Structural Change Detection
  "changepoint",     # Changepoint Detection
  "segmented"        # Regression Models with Breakpoints
)

# Visualization
viz_packages <- c(
  "ggplot2",         # Grammar of Graphics
  "plotly",          # Interactive plots
  "ggthemes",        # Additional themes for ggplot2
  "ggrepel",         # Repulsive text labels
  "ggpubr",          # Publication ready plots
  "corrplot",        # Correlation matrix visualization
  "RColorBrewer",    # Color palettes
  "viridis",         # Colorblind-friendly palettes
  "scales",          # Scale functions for visualization
  "gridExtra",       # Grid graphics
  "patchwork",       # Combine ggplot2 plots
  "ggmap",           # Maps with ggplot2
  "leaflet",         # Interactive maps
  "sf",              # Simple features for spatial data
  "maps",            # Draw geographical maps
  "mapdata"          # Map databases
)

# Machine Learning and Advanced Analytics
ml_packages <- c(
  "caret",           # Classification and Regression Training
  "randomForest",    # Random Forest
  "e1071",           # Support Vector Machines
  "nnet",            # Neural Networks
  "glmnet",          # Lasso and Elastic-Net
  "rpart",           # Recursive Partitioning
  "rpart.plot",      # Plot rpart trees
  "gbm",             # Gradient Boosting
  "xgboost",         # Extreme Gradient Boosting
  "cluster",         # Cluster Analysis
  "factoextra",      # Extract and Visualize Results
  "NbClust",         # Determining the Best Number of Clusters
  "fpc",             # Flexible Procedures for Clustering
  "dbscan"           # Density-Based Clustering
)

# Time Series and Econometrics
ts_packages <- c(
  "zoo",             # Z's Ordered Observations
  "xts",             # Extensible Time Series
  "quantmod",        # Quantitative Financial Modelling
  "PerformanceAnalytics", # Econometric tools for performance analysis
  "rugarch",         # Univariate GARCH models
  "fGarch",          # Financial GARCH models
  "copula",          # Multivariate Dependence with Copulas
  "evir",            # Extreme Values in R
  "ismev",           # Introduction to Statistical Modelling of Extreme Values
  "extRemes"         # Extreme Value Analysis
)

# Database and API Connectivity
db_packages <- c(
  "DBI",             # Database Interface
  "RSQLite",         # SQLite interface
  "RPostgreSQL",     # PostgreSQL interface
  "RODBC",           # ODBC database access
  "jsonlite",        # JSON parser
  "httr",            # HTTP requests
  "xml2",            # XML parsing
  "rvest",           # Web scraping
  "RSelenium"        # Selenium WebDriver
)

# Reporting and Documentation
report_packages <- c(
  "rmarkdown",       # Dynamic documents
  "knitr",           # Dynamic report generation
  "DT",              # DataTables for R
  "shiny",           # Web application framework
  "shinydashboard",  # Dashboard for Shiny
  "flexdashboard",   # R Markdown dashboards
  "kableExtra",      # Enhanced table formatting
  "formattable",     # Formattable data structures
  "gt",              # Grammar of tables
  "flextable",       # Flexible table creation
  "officer",         # Manipulation of Word and PowerPoint documents
  "openxlsx"         # Read, write and edit Excel files
)

# Install all packages
cat("Installing core packages...\n")
install_if_missing(core_packages)

cat("Installing statistical analysis packages...\n")
install_if_missing(stats_packages)

cat("Installing visualization packages...\n")
install_if_missing(viz_packages)

cat("Installing machine learning packages...\n")
install_if_missing(ml_packages)

cat("Installing time series packages...\n")
install_if_missing(ts_packages)

cat("Installing database connectivity packages...\n")
install_if_missing(db_packages)

cat("Installing reporting packages...\n")
install_if_missing(report_packages)

cat("All packages installed successfully!\n")

# Verify installations
cat("\nVerifying installations...\n")
all_packages <- c(core_packages, stats_packages, viz_packages, 
                  ml_packages, ts_packages, db_packages, report_packages)

missing_packages <- c()
for (package in all_packages) {
  if (!require(package, character.only = TRUE, quietly = TRUE)) {
    missing_packages <- c(missing_packages, package)
  }
}

if (length(missing_packages) > 0) {
  cat("Warning: The following packages could not be loaded:\n")
  cat(paste(missing_packages, collapse = ", "), "\n")
} else {
  cat("All packages loaded successfully!\n")
} 