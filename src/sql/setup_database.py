#!/usr/bin/env python3
"""
Database Setup Script for Trade Analysis Dashboard
Creates SQLite database with all necessary tables for storing trade data,
economic indicators, tariffs, sanctions, and analysis results.
"""

import sqlite3
import os
import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

def create_database():
    """Create the SQLite database and all necessary tables."""
    
    # Create data directory if it doesn't exist
    data_dir = project_root / "data" / "sql"
    data_dir.mkdir(parents=True, exist_ok=True)
    
    db_path = data_dir / "trade_analysis.db"
    
    # Connect to SQLite database (creates it if it doesn't exist)
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print(f"Creating database at: {db_path}")
    
    # Create tables
    create_countries_table(cursor)
    create_trade_data_table(cursor)
    create_economic_indicators_table(cursor)
    create_tariffs_table(cursor)
    create_sanctions_table(cursor)
    create_trade_policies_table(cursor)
    create_environmental_metrics_table(cursor)
    create_sectors_table(cursor)
    create_analysis_results_table(cursor)
    create_scenarios_table(cursor)
    create_risk_scores_table(cursor)
    
    # Commit changes and close connection
    conn.commit()
    conn.close()
    
    print("Database setup completed successfully!")
    return db_path

def create_countries_table(cursor):
    """Create countries table."""
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS countries (
            country_id INTEGER PRIMARY KEY AUTOINCREMENT,
            country_code TEXT UNIQUE NOT NULL,
            country_name TEXT NOT NULL,
            region TEXT,
            income_group TEXT,
            gdp_2022 REAL,
            population_2022 INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    print("Created countries table")

def create_trade_data_table(cursor):
    """Create trade data table."""
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS trade_data (
            trade_id INTEGER PRIMARY KEY AUTOINCREMENT,
            year INTEGER NOT NULL,
            month INTEGER,
            reporter_country_id INTEGER,
            partner_country_id INTEGER,
            commodity_code TEXT,
            commodity_description TEXT,
            trade_flow TEXT CHECK(trade_flow IN ('import', 'export')),
            value_usd REAL,
            quantity REAL,
            unit TEXT,
            source TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (reporter_country_id) REFERENCES countries (country_id),
            FOREIGN KEY (partner_country_id) REFERENCES countries (country_id)
        )
    ''')
    print("Created trade_data table")

def create_economic_indicators_table(cursor):
    """Create economic indicators table."""
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS economic_indicators (
            indicator_id INTEGER PRIMARY KEY AUTOINCREMENT,
            country_id INTEGER,
            year INTEGER NOT NULL,
            quarter INTEGER,
            indicator_name TEXT NOT NULL,
            indicator_value REAL,
            unit TEXT,
            source TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (country_id) REFERENCES countries (country_id)
        )
    ''')
    print("Created economic_indicators table")

def create_tariffs_table(cursor):
    """Create tariffs table."""
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tariffs (
            tariff_id INTEGER PRIMARY KEY AUTOINCREMENT,
            country_id INTEGER,
            partner_country_id INTEGER,
            commodity_code TEXT,
            tariff_rate REAL,
            tariff_type TEXT CHECK(tariff_type IN ('MFN', 'preferential', 'safeguard')),
            effective_date DATE,
            expiry_date DATE,
            source TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (country_id) REFERENCES countries (country_id),
            FOREIGN KEY (partner_country_id) REFERENCES countries (country_id)
        )
    ''')
    print("Created tariffs table")

def create_sanctions_table(cursor):
    """Create sanctions table."""
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sanctions (
            sanction_id INTEGER PRIMARY KEY AUTOINCREMENT,
            sanctioning_country_id INTEGER,
            target_country_id INTEGER,
            sanction_type TEXT CHECK(sanction_type IN ('trade', 'financial', 'travel', 'arms', 'other')),
            description TEXT,
            start_date DATE,
            end_date DATE,
            status TEXT CHECK(status IN ('active', 'suspended', 'lifted')),
            source TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (sanctioning_country_id) REFERENCES countries (country_id),
            FOREIGN KEY (target_country_id) REFERENCES countries (country_id)
        )
    ''')
    print("Created sanctions table")

def create_trade_policies_table(cursor):
    """Create trade policies table."""
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS trade_policies (
            policy_id INTEGER PRIMARY KEY AUTOINCREMENT,
            country_id INTEGER,
            policy_name TEXT NOT NULL,
            policy_type TEXT CHECK(policy_type IN ('tariff', 'quota', 'subsidy', 'regulation', 'agreement', 'carbon_tariff', 'green_agreement', 'circular_policy')),
            description TEXT,
            effective_date DATE,
            expiry_date DATE,
            status TEXT CHECK(status IN ('active', 'proposed', 'expired')),
            source TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (country_id) REFERENCES countries (country_id)
        )
    ''')
    print("Created trade_policies table")

def create_environmental_metrics_table(cursor):
    """Create environmental metrics table."""
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS environmental_metrics (
            metric_id INTEGER PRIMARY KEY AUTOINCREMENT,
            country_id INTEGER,
            year INTEGER NOT NULL,
            carbon_intensity REAL,  -- CO2 emissions per $ of trade
            green_trade_share REAL,  -- % of trade in renewable/green sectors
            transport_emissions REAL,  -- CO2 from trade transport (million tons)
            circular_economy_score REAL,  -- 0-100 score for circular economy practices
            renewable_energy_trade REAL,  -- Renewable energy trade volume ($ millions)
            carbon_footprint REAL,  -- Total CO2 emissions from trade (million tons)
            source TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (country_id) REFERENCES countries (country_id)
        )
    ''')
    print("Created environmental_metrics table")

def create_sectors_table(cursor):
    """Create sectors table."""
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sectors (
            sector_id INTEGER PRIMARY KEY AUTOINCREMENT,
            sector_code TEXT UNIQUE NOT NULL,
            sector_name TEXT NOT NULL,
            parent_sector_id INTEGER,
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (parent_sector_id) REFERENCES sectors (sector_id)
        )
    ''')
    print("Created sectors table")

def create_analysis_results_table(cursor):
    """Create analysis results table."""
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS analysis_results (
            result_id INTEGER PRIMARY KEY AUTOINCREMENT,
            analysis_type TEXT NOT NULL,
            country_id INTEGER,
            partner_country_id INTEGER,
            sector_id INTEGER,
            analysis_date DATE,
            model_used TEXT,
            parameters TEXT,  -- JSON string of model parameters
            results TEXT,     -- JSON string of results
            confidence_interval REAL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (country_id) REFERENCES countries (country_id),
            FOREIGN KEY (partner_country_id) REFERENCES countries (country_id),
            FOREIGN KEY (sector_id) REFERENCES sectors (sector_id)
        )
    ''')
    print("Created analysis_results table")

def create_scenarios_table(cursor):
    """Create scenarios table."""
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS scenarios (
            scenario_id INTEGER PRIMARY KEY AUTOINCREMENT,
            scenario_name TEXT NOT NULL,
            scenario_description TEXT,
            scenario_type TEXT CHECK(scenario_type IN ('tariff_change', 'sanction_impact', 'policy_change', 'economic_shock')),
            base_year INTEGER,
            projection_years INTEGER,
            parameters TEXT,  -- JSON string of scenario parameters
            created_by TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    print("Created scenarios table")

def create_risk_scores_table(cursor):
    """Create risk scores table."""
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS risk_scores (
            risk_id INTEGER PRIMARY KEY AUTOINCREMENT,
            country_id INTEGER,
            risk_type TEXT CHECK(risk_type IN ('trade_risk', 'policy_risk', 'economic_risk', 'sanction_risk')),
            risk_score REAL CHECK(risk_score >= 0 AND risk_score <= 100),
            risk_factors TEXT,  -- JSON string of contributing factors
            assessment_date DATE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (country_id) REFERENCES countries (country_id)
        )
    ''')
    print("Created risk_scores table")

def insert_sample_data(cursor):
    """Insert sample data for testing."""
    
    # Insert sample countries
    countries = [
        ('USA', 'United States', 'North America', 'High income', 25462700, 331002651),
        ('CHN', 'China', 'Asia', 'Upper middle income', 17963170, 1439323776),
        ('DEU', 'Germany', 'Europe', 'High income', 4072191, 83190556),
        ('JPN', 'Japan', 'Asia', 'High income', 4231141, 125836021),
        ('GBR', 'United Kingdom', 'Europe', 'High income', 3070667, 67215293),
        ('CAN', 'Canada', 'North America', 'High income', 2139840, 37742154),
        ('FRA', 'France', 'Europe', 'High income', 2782905, 65273511),
        ('ITA', 'Italy', 'Europe', 'High income', 2010430, 60461826),
        ('BRA', 'Brazil', 'South America', 'Upper middle income', 1920095, 212559417),
        ('IND', 'India', 'Asia', 'Lower middle income', 3385090, 1380004385)
    ]
    
    cursor.executemany('''
        INSERT OR IGNORE INTO countries 
        (country_code, country_name, region, income_group, gdp_2022, population_2022)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', countries)
    
    print("Inserted sample countries")

def create_indexes(cursor):
    """Create indexes for better query performance."""
    
    indexes = [
        "CREATE INDEX IF NOT EXISTS idx_trade_data_year ON trade_data(year)",
        "CREATE INDEX IF NOT EXISTS idx_trade_data_countries ON trade_data(reporter_country_id, partner_country_id)",
        "CREATE INDEX IF NOT EXISTS idx_trade_data_flow ON trade_data(trade_flow)",
        "CREATE INDEX IF NOT EXISTS idx_economic_indicators_country_year ON economic_indicators(country_id, year)",
        "CREATE INDEX IF NOT EXISTS idx_tariffs_countries ON tariffs(country_id, partner_country_id)",
        "CREATE INDEX IF NOT EXISTS idx_sanctions_target ON sanctions(target_country_id)",
        "CREATE INDEX IF NOT EXISTS idx_analysis_results_type_date ON analysis_results(analysis_type, analysis_date)",
        "CREATE INDEX IF NOT EXISTS idx_risk_scores_country_type ON risk_scores(country_id, risk_type)"
    ]
    
    for index_sql in indexes:
        cursor.execute(index_sql)
    
    print("Created database indexes")

if __name__ == "__main__":
    try:
        db_path = create_database()
        
        # Connect again to add sample data and indexes
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        insert_sample_data(cursor)
        create_indexes(cursor)
        
        conn.commit()
        conn.close()
        
        print(f"\nDatabase setup completed successfully!")
        print(f"Database location: {db_path}")
        print("\nNext steps:")
        print("1. Run data collection scripts")
        print("2. Process and clean the data")
        print("3. Generate analysis and visualizations")
        
    except Exception as e:
        print(f"Error setting up database: {e}")
        sys.exit(1) 