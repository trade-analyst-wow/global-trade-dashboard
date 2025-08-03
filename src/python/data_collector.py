#!/usr/bin/env python3
"""
Data Collector for Trade Analysis Dashboard
Collects trade data, economic indicators, tariffs, and sanctions data from various sources.
"""

import requests
import pandas as pd
import sqlite3
import json
import time
from datetime import datetime, timedelta
from pathlib import Path
import sys
import logging
from typing import Dict, List, Optional, Tuple
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add the project root to the Python path
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(project_root / 'logs' / 'data_collection.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class TradeDataCollector:
    """Main class for collecting trade and economic data."""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Trade Analysis Dashboard/1.0'
        })
        
        # API keys (should be stored in environment variables)
        self.world_bank_api_key = os.getenv('WORLD_BANK_API_KEY')
        self.imf_api_key = os.getenv('IMF_API_KEY')
        self.oecd_api_key = os.getenv('OECD_API_KEY')
        self.comtrade_api_key = os.getenv('COMTRADE_API_KEY', '303fffa880a44d74af8a1badc10e4eae')
        
        # Free APIs (no authentication required)
        self.fred_api_key = os.getenv('FRED_API_KEY')  # Federal Reserve Economic Data
        self.alpha_vantage_api_key = os.getenv('ALPHA_VANTAGE_API_KEY')  # Financial data
        
        # Rate limiting
        self.request_delay = 1  # seconds between requests
        
    def collect_all_data(self, start_year: int = 2020, end_year: int = 2023):
        """Collect all types of data."""
        logger.info("Starting comprehensive data collection...")
        
        try:
            # Collect trade data
            self.collect_trade_data(start_year, end_year)
            
            # Collect economic indicators
            self.collect_economic_indicators(start_year, end_year)
            
            # Collect environmental data
            self.collect_environmental_data(start_year, end_year)
            
            # Collect tariff data
            self.collect_tariff_data()
            
            # Collect sanctions data
            self.collect_sanctions_data()
            
            # Collect policy data
            self.collect_policy_data()
            
            logger.info("Data collection completed successfully!")
            
        except Exception as e:
            logger.error(f"Error during data collection: {e}")
            raise
    
    def collect_trade_data(self, start_year: int, end_year: int):
        """Collect trade data from multiple sources and generate sample data."""
        logger.info("Collecting trade data from multiple sources...")
        
        # Generate comprehensive sample trade data (faster than API calls)
        self._generate_sample_trade_data(start_year, end_year)
        
        # Try to collect from World Bank (free, no API key needed) - optional
        # self._collect_world_bank_trade_data(start_year, end_year)
    
    def _collect_comtrade_data(self, country: str, year: int, flow: str):
        """Collect data from UN Comtrade Public API."""
        
        # UN Comtrade Public API endpoint (no authentication required)
        base_url = "https://comtradeapi.un.org/public/v1/getComtradeData"
        
        params = {
            'r': self._get_country_code(country),
            'ps': year,
            'px': 'HS',
            'p': 0,  # World
            'rg': 1 if flow == 'import' else 2,  # 1=import, 2=export
            'cc': 'TOTAL',
            'fmt': 'json'
        }
        
        try:
            response = self.session.get(base_url, params=params)
            response.raise_for_status()
            
            data = response.json()
            
            if 'data' in data and data['data']:
                self._save_trade_data(data['data'], country, year, flow)
                
        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed for {country} {year} {flow}: {e}")
    
    def collect_economic_indicators(self, start_year: int, end_year: int):
        """Collect economic indicators from multiple sources."""
        logger.info("Collecting economic indicators from multiple sources...")
        
        # Use sample data for faster setup (World Bank API is slow)
        logger.info("Using sample economic data for faster setup...")
        self._generate_sample_economic_data(start_year, end_year)
        
        # Optional: Uncomment to try World Bank API (slower but real data)
        # try:
        #     logger.info("Attempting to collect from World Bank API...")
        #     self._collect_world_bank_indicators(start_year, end_year)
        #     logger.info("Successfully collected World Bank data")
        # except Exception as e:
        #     logger.warning(f"World Bank collection failed: {e}")
        
        # Collect from FRED (Federal Reserve Economic Data - free with API key)
        if self.fred_api_key:
            try:
                self._collect_fred_indicators(start_year, end_year)
            except Exception as e:
                logger.warning(f"FRED collection failed: {e}")
    
    def _collect_world_bank_indicators(self, start_year: int, end_year: int):
        """Collect economic indicators from World Bank API."""
        logger.info("Collecting economic indicators from World Bank...")
        
        # Key economic indicators
        indicators = {
            'NY.GDP.MKTP.CD': 'GDP (current US$)',
            'NY.GDP.MKTP.KD.ZG': 'GDP growth (annual %)',
            'SL.UEM.TOTL.ZS': 'Unemployment, total (% of total labor force)',
            'FP.CPI.TOTL.ZG': 'Inflation, consumer prices (annual %)',
            'NE.EXP.GNFS.ZS': 'Exports of goods and services (% of GDP)',
            'NE.IMP.GNFS.ZS': 'Imports of goods and services (% of GDP)',
            'NE.RSB.GNFS.ZS': 'External balance on goods and services (% of GDP)'
        }
        
        countries = ['US', 'CN', 'DE', 'JP', 'GB', 'CA', 'FR', 'IT', 'BR', 'IN']
        
        for indicator_code, indicator_name in indicators.items():
            for country in countries:
                try:
                    self._collect_world_bank_data(indicator_code, country, start_year, end_year)
                    time.sleep(self.request_delay)
                except Exception as e:
                    logger.error(f"Error collecting {indicator_code} for {country}: {e}")
                    continue
    
    def _collect_fred_indicators(self, start_year: int, end_year: int):
        """Collect economic indicators from FRED API."""
        logger.info("Collecting economic indicators from FRED...")
        
        # FRED series for US economic data
        fred_series = {
            'GDP': 'Gross Domestic Product',
            'UNRATE': 'Unemployment Rate',
            'CPIAUCSL': 'Consumer Price Index',
            'EXUSEU': 'US/Euro Exchange Rate',
            'DGS10': '10-Year Treasury Rate'
        }
        
        for series_id, description in fred_series.items():
            try:
                self._collect_fred_data(series_id, start_year, end_year)
                time.sleep(self.request_delay)
            except Exception as e:
                logger.error(f"Error collecting FRED data for {series_id}: {e}")
                continue
    
    def _collect_world_bank_trade_data(self, start_year: int, end_year: int):
        """Collect trade data from World Bank API."""
        logger.info("Collecting trade data from World Bank...")
        
        # Trade-related indicators
        trade_indicators = {
            'NE.EXP.GNFS.CD': 'Exports of goods and services (current US$)',
            'NE.IMP.GNFS.CD': 'Imports of goods and services (current US$)',
            'NE.EXP.GNFS.ZS': 'Exports of goods and services (% of GDP)',
            'NE.IMP.GNFS.ZS': 'Imports of goods and services (% of GDP)',
            'NE.RSB.GNFS.ZS': 'External balance on goods and services (% of GDP)'
        }
        
        countries = ['US', 'CN', 'DE', 'JP', 'GB', 'CA', 'FR', 'IT', 'BR', 'IN']
        
        for indicator_code, indicator_name in trade_indicators.items():
            for country in countries:
                try:
                    self._collect_world_bank_data(indicator_code, country, start_year, end_year)
                    time.sleep(self.request_delay)
                except Exception as e:
                    logger.error(f"Error collecting trade data {indicator_code} for {country}: {e}")
                    continue
    
    def _generate_sample_trade_data(self, start_year: int, end_year: int):
        """Generate comprehensive sample trade data."""
        logger.info("Generating sample trade data...")
        
        # Major trading countries with realistic trade values
        countries = [
            ('USA', 'United States', 25000000, 30000000),  # (imports, exports) in millions USD
            ('CHN', 'China', 28000000, 35000000),
            ('DEU', 'Germany', 15000000, 18000000),
            ('JPN', 'Japan', 8000000, 10000000),
            ('GBR', 'United Kingdom', 7000000, 8000000),
            ('CAN', 'Canada', 5000000, 6000000),
            ('FRA', 'France', 6000000, 7000000),
            ('ITA', 'Italy', 5000000, 6000000),
            ('BRA', 'Brazil', 3000000, 4000000),
            ('IND', 'India', 4000000, 5000000)
        ]
        
        # Partner countries for bilateral trade
        partner_countries = [
            ('USA', 'United States', 1),
            ('CHN', 'China', 2),
            ('DEU', 'Germany', 3),
            ('JPN', 'Japan', 4),
            ('GBR', 'United Kingdom', 5),
            ('CAN', 'Canada', 6),
            ('FRA', 'France', 7),
            ('ITA', 'Italy', 8),
            ('BRA', 'Brazil', 9),
            ('IND', 'India', 10)
        ]
        
        sample_data = []
        
        for year in range(start_year, end_year + 1):
            for country_code, country_name, base_imports, base_exports in countries:
                reporter_id = self._get_country_id(country_code)
                
                # Generate total trade data (with World as partner)
                import_variation = 1 + (year - start_year) * 0.05 + (hash(f"{country_code}{year}") % 100 - 50) / 1000
                export_variation = 1 + (year - start_year) * 0.06 + (hash(f"{country_code}{year}") % 100 - 50) / 1000
                
                # Generate import data
                import_value = base_imports * import_variation
                sample_data.append({
                    'year': year,
                    'reporter_country_id': reporter_id,
                    'partner_country_id': 0,  # World
                    'trade_flow': 'import',
                    'value_usd': import_value,
                    'source': 'Sample Data'
                })
                
                # Generate export data
                export_value = base_exports * export_variation
                sample_data.append({
                    'year': year,
                    'reporter_country_id': reporter_id,
                    'partner_country_id': 0,  # World
                    'trade_flow': 'export',
                    'value_usd': export_value,
                    'source': 'Sample Data'
                })
                
                # Generate bilateral trade data with other countries
                for partner_code, partner_name, partner_id in partner_countries:
                    if partner_code != country_code:
                        # Bilateral trade is typically smaller than total trade
                        bilateral_factor = 0.1 + (hash(f"{country_code}{partner_code}{year}") % 50) / 1000
                        
                        # Generate bilateral imports
                        bilateral_import = import_value * bilateral_factor
                        sample_data.append({
                            'year': year,
                            'reporter_country_id': reporter_id,
                            'partner_country_id': partner_id,
                            'trade_flow': 'import',
                            'value_usd': bilateral_import,
                            'source': 'Sample Data'
                        })
                        
                        # Generate bilateral exports
                        bilateral_export = export_value * bilateral_factor
                        sample_data.append({
                            'year': year,
                            'reporter_country_id': reporter_id,
                            'partner_country_id': partner_id,
                            'trade_flow': 'export',
                            'value_usd': bilateral_export,
                            'source': 'Sample Data'
                        })
        
        self._save_sample_trade_data(sample_data)
        logger.info(f"Generated {len(sample_data)} sample trade records")
    
    def _collect_world_bank_data(self, indicator: str, country: str, start_year: int, end_year: int):
        """Collect data from World Bank API."""
        
        base_url = "https://api.worldbank.org/v2/country"
        
        params = {
            'format': 'json',
            'per_page': 1000,
            'date': f"{start_year}:{end_year}"
        }
        
        url = f"{base_url}/{country}/indicator/{indicator}"
        
        try:
            response = self.session.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            
            if len(data) > 1 and data[1]:
                self._save_economic_indicators(data[1], country, indicator)
                
        except requests.exceptions.RequestException as e:
            logger.error(f"World Bank API request failed for {indicator} {country}: {e}")
    
    def _collect_fred_data(self, series_id: str, start_year: int, end_year: int):
        """Collect data from FRED API."""
        
        base_url = "https://api.stlouisfed.org/fred/series/observations"
        
        params = {
            'series_id': series_id,
            'api_key': self.fred_api_key,
            'file_type': 'json',
            'observation_start': f"{start_year}-01-01",
            'observation_end': f"{end_year}-12-31"
        }
        
        try:
            response = self.session.get(base_url, params=params)
            response.raise_for_status()
            
            data = response.json()
            
            if 'observations' in data:
                self._save_fred_data(data['observations'], series_id)
                
        except requests.exceptions.RequestException as e:
            logger.error(f"FRED API request failed for {series_id}: {e}")
    
    def _generate_sample_economic_data(self, start_year: int, end_year: int):
        """Generate comprehensive sample economic data."""
        logger.info("Generating sample economic data...")
        
        # Economic indicators with realistic values - ONLY UNIQUE INDICATORS
        indicators = {
            'GDP (current US$)': {'base': 2000000, 'growth': 0.03},  # Millions USD
            'GDP growth (annual %)': {'base': 2.5, 'growth': 0.1},   # Percentage
            'Unemployment Rate (%)': {'base': 5.0, 'growth': -0.2},  # Percentage
            'Inflation Rate (%)': {'base': 2.0, 'growth': 0.1},  # Percentage
            'Exports (% of GDP)': {'base': 25.0, 'growth': 0.5},  # Percentage
            'Imports (% of GDP)': {'base': 22.0, 'growth': 0.3},  # Percentage
            'Trade Balance (% of GDP)': {'base': 3.0, 'growth': 0.2}  # Percentage
        }
        
        countries = [
            ('USA', 'United States', 1),
            ('CHN', 'China', 2),
            ('DEU', 'Germany', 3),
            ('JPN', 'Japan', 4),
            ('GBR', 'United Kingdom', 5),
            ('CAN', 'Canada', 6),
            ('FRA', 'France', 7),
            ('ITA', 'Italy', 8),
            ('BRA', 'Brazil', 9),
            ('IND', 'India', 10)
        ]
        
        sample_data = []
        
        for year in range(start_year, end_year + 1):
            for country_code, country_name, country_id in countries:
                for indicator_name, params in indicators.items():
                    # Add realistic variation based on year and country
                    variation = 1 + (year - start_year) * params['growth'] + (hash(f"{country_code}{indicator_name}{year}") % 100 - 50) / 1000
                    value = params['base'] * variation
                    
                    sample_data.append({
                        'country_id': country_id,
                        'year': year,
                        'indicator_name': indicator_name,
                        'indicator_value': value,
                        'source': 'Sample Data'
                    })
        
        self._save_sample_economic_data(sample_data)
        logger.info(f"Generated {len(sample_data)} sample economic records")
    
    def _save_sample_economic_data(self, data: List[Dict]):
        """Save sample economic data to database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        for record in data:
            try:
                cursor.execute('''
                    INSERT OR REPLACE INTO economic_indicators 
                    (country_id, year, indicator_name, indicator_value, source)
                    VALUES (?, ?, ?, ?, ?)
                ''', (
                    record['country_id'],
                    record['year'],
                    record['indicator_name'],
                    record['indicator_value'],
                    record['source']
                ))
            except Exception as e:
                logger.error(f"Error saving sample economic data: {e}")
                continue
        
        conn.commit()
        conn.close()
    
    def _save_fred_data(self, observations: List[Dict], series_id: str):
        """Save FRED data to database."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            for obs in observations:
                if obs.get('value') != '.' and obs.get('value'):  # Skip missing values
                    cursor.execute('''
                        INSERT OR REPLACE INTO economic_indicators 
                        (country_id, year, indicator_name, indicator_value, source)
                        VALUES (?, ?, ?, ?, ?)
                    ''', (
                        1,  # US country_id
                        int(obs['date'][:4]),  # Extract year from date
                        f"FRED_{series_id}",
                        float(obs['value']),
                        'FRED'
                    ))
            
            conn.commit()
            conn.close()
            logger.info(f"Saved {len(observations)} FRED observations for {series_id}")
            
        except Exception as e:
            logger.error(f"Error saving FRED data: {e}")
    
    def collect_tariff_data(self):
        """Collect tariff data from WTO and other sources."""
        logger.info("Collecting tariff data...")
        
        # This would typically involve scraping WTO tariff databases
        # For now, we'll create sample data
        sample_tariffs = self._generate_sample_tariff_data()
        self._save_tariff_data(sample_tariffs)
    
    def collect_sanctions_data(self):
        """Collect sanctions data from various sources."""
        logger.info("Collecting sanctions data...")
        
        # This would involve scraping UN Security Council and OFAC databases
        # For now, we'll create sample data
        sample_sanctions = self._generate_sample_sanctions_data()
        self._save_sanctions_data(sample_sanctions)
    
    def collect_environmental_data(self, start_year: int, end_year: int):
        """Collect environmental sustainability data."""
        logger.info("Collecting environmental sustainability data...")
        
        # Generate sample environmental data
        self._generate_sample_environmental_data(start_year, end_year)
    
    def collect_policy_data(self):
        """Collect trade policy data."""
        logger.info("Collecting trade policy data...")
        
        # This would involve scraping government databases and trade agreements
        # For now, we'll create sample data
        sample_policies = self._generate_sample_policy_data()
        self._save_policy_data(sample_policies)
    
    def _get_country_code(self, country: str) -> str:
        """Convert country name to UN Comtrade country code."""
        country_codes = {
            'USA': '842', 'CHN': '156', 'DEU': '276', 'JPN': '392',
            'GBR': '826', 'CAN': '124', 'FRA': '250', 'ITA': '380',
            'BRA': '076', 'IND': '356'
        }
        return country_codes.get(country, '000')
    
    def _save_trade_data(self, data: List[Dict], country: str, year: int, flow: str):
        """Save trade data to database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        for record in data:
            try:
                cursor.execute('''
                    INSERT OR REPLACE INTO trade_data 
                    (year, reporter_country_id, partner_country_id, commodity_code, 
                     commodity_description, trade_flow, value_usd, quantity, unit, source)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    year,
                    self._get_country_id(country),
                    self._get_country_id(record.get('ptTitle', 'World')),
                    record.get('cmdCode', 'TOTAL'),
                    record.get('cmdDescE', ''),
                    flow,
                    record.get('TradeValue', 0),
                    record.get('NetWgt', 0),
                    record.get('qtyUnitAbbr', ''),
                    'UN Comtrade'
                ))
            except Exception as e:
                logger.error(f"Error saving trade data: {e}")
                continue
        
        conn.commit()
        conn.close()
    
    def _save_economic_indicators(self, data: List[Dict], country: str, indicator: str):
        """Save economic indicators to database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        for record in data:
            try:
                cursor.execute('''
                    INSERT OR REPLACE INTO economic_indicators 
                    (country_id, year, indicator_name, indicator_value, source)
                    VALUES (?, ?, ?, ?, ?)
                ''', (
                    self._get_country_id(country),
                    record.get('date'),
                    indicator,
                    record.get('value'),
                    'World Bank'
                ))
            except Exception as e:
                logger.error(f"Error saving economic indicator: {e}")
                continue
        
        conn.commit()
        conn.close()
    
    def _save_sample_trade_data(self, data: List[Dict]):
        """Save sample trade data to database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        for record in data:
            try:
                cursor.execute('''
                    INSERT OR REPLACE INTO trade_data 
                    (year, reporter_country_id, partner_country_id, commodity_code, 
                     commodity_description, trade_flow, value_usd, source)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    record['year'],
                    record['reporter_country_id'],
                    record['partner_country_id'],
                    'TOTAL',
                    'Total Trade',
                    record['trade_flow'],
                    record['value_usd'],
                    record['source']
                ))
            except Exception as e:
                logger.error(f"Error saving sample trade data: {e}")
                continue
        
        conn.commit()
        conn.close()
    
    def _get_country_id(self, country_code: str) -> int:
        """Get country ID from database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT country_id FROM countries WHERE country_code = ?', (country_code,))
        result = cursor.fetchone()
        
        conn.close()
        
        return result[0] if result else 1  # Default to first country if not found
    
    def _generate_sample_tariff_data(self) -> List[Dict]:
        """Generate sample tariff data for demonstration."""
        return [
            {
                'country_id': 1, 'partner_country_id': 2, 'commodity_code': '0101',
                'tariff_rate': 2.5, 'tariff_type': 'MFN', 'effective_date': '2023-01-01',
                'source': 'WTO'
            },
            {
                'country_id': 1, 'partner_country_id': 3, 'commodity_code': '0101',
                'tariff_rate': 0.0, 'tariff_type': 'preferential', 'effective_date': '2023-01-01',
                'source': 'WTO'
            }
        ]
    
    def _generate_sample_sanctions_data(self) -> List[Dict]:
        """Generate realistic sample sanctions data."""
        return [
            # China sanctions (current)
            {
                'sanctioning_country_id': 1, 'target_country_id': 2,  # US -> China
                'sanction_type': 'trade', 
                'description': 'Semiconductor export controls and advanced technology restrictions',
                'start_date': '2022-10-07', 'status': 'active', 'source': 'BIS'
            },
            {
                'sanctioning_country_id': 1, 'target_country_id': 2,  # US -> China
                'sanction_type': 'financial', 
                'description': 'Entity List restrictions on Huawei, SMIC, and other tech companies',
                'start_date': '2023-08-01', 'status': 'active', 'source': 'OFAC'
            },
            # Brazil sanctions (current)
            {
                'sanctioning_country_id': 1, 'target_country_id': 9,  # US -> Brazil
                'sanction_type': 'trade', 
                'description': 'Ongoing steel and aluminum tariff restrictions',
                'start_date': '2021-01-15', 'status': 'active', 'source': 'USTR'
            },
            {
                'sanctioning_country_id': 1, 'target_country_id': 9,  # US -> Brazil
                'sanction_type': 'financial', 
                'description': 'Financial restrictions on Brazilian companies in US markets',
                'start_date': '2023-08-15', 'status': 'active', 'source': 'OFAC'
            },
            # Russia sanctions (ongoing)
            {
                'sanctioning_country_id': 1, 'target_country_id': 3,  # US -> Germany
                'sanction_type': 'financial', 
                'description': 'Secondary sanctions on Nord Stream 2 pipeline companies',
                'start_date': '2021-05-19', 'status': 'active', 'source': 'OFAC'
            },
            # India sanctions (CAATSA - ongoing)
            {
                'sanctioning_country_id': 1, 'target_country_id': 10,  # US -> India
                'sanction_type': 'arms', 
                'description': 'CAATSA sanctions for S-400 missile system purchase from Russia',
                'start_date': '2021-12-14', 'status': 'active', 'source': 'CAATSA'
            },
            # EU sanctions on Russia (affecting trade)
            {
                'sanctioning_country_id': 4, 'target_country_id': 3,  # Germany -> Russia
                'sanction_type': 'trade', 
                'description': 'EU sanctions on Russian oil and gas imports',
                'start_date': '2022-06-03', 'status': 'active', 'source': 'EU'
            },
            # US sanctions on Iran (affecting trade partners)
            {
                'sanctioning_country_id': 1, 'target_country_id': 2,  # US -> China
                'sanction_type': 'financial', 
                'description': 'Secondary sanctions on Chinese companies trading with Iran',
                'start_date': '2023-11-02', 'status': 'active', 'source': 'OFAC'
            }
        ]
    
    def _generate_sample_environmental_data(self, start_year: int, end_year: int):
        """Generate realistic sample environmental sustainability data."""
        logger.info("Generating sample environmental data...")
        
        # Environmental metrics with realistic values
        countries = [
            ('USA', 'United States', 1),
            ('CHN', 'China', 2),
            ('DEU', 'Germany', 3),
            ('JPN', 'Japan', 4),
            ('GBR', 'United Kingdom', 5),
            ('CAN', 'Canada', 6),
            ('FRA', 'France', 7),
            ('ITA', 'Italy', 8),
            ('BRA', 'Brazil', 9),
            ('IND', 'India', 10)
        ]
        
        environmental_data = []
        
        for year in range(start_year, end_year + 1):
            for country_code, country_name, country_id in countries:
                # Generate realistic environmental metrics based on country characteristics
                if country_code == 'CHN':  # China - high carbon intensity
                    carbon_intensity = 0.8 + (hash(f"{country_code}{year}") % 100) / 1000
                    green_trade_share = 15.0 + (year - start_year) * 2.0  # Improving
                    transport_emissions = 45.0 + (hash(f"{country_code}{year}") % 50) / 10
                    circular_score = 35.0 + (year - start_year) * 3.0
                    renewable_trade = 25.0 + (year - start_year) * 5.0
                    carbon_footprint = 120.0 + (hash(f"{country_code}{year}") % 100) / 10
                
                elif country_code == 'DEU':  # Germany - green leader
                    carbon_intensity = 0.3 + (hash(f"{country_code}{year}") % 100) / 1000
                    green_trade_share = 45.0 + (year - start_year) * 3.0
                    transport_emissions = 25.0 + (hash(f"{country_code}{year}") % 30) / 10
                    circular_score = 75.0 + (year - start_year) * 2.0
                    renewable_trade = 85.0 + (year - start_year) * 3.0
                    carbon_footprint = 45.0 + (hash(f"{country_code}{year}") % 50) / 10
                
                elif country_code == 'USA':  # US - moderate
                    carbon_intensity = 0.5 + (hash(f"{country_code}{year}") % 100) / 1000
                    green_trade_share = 25.0 + (year - start_year) * 2.5
                    transport_emissions = 35.0 + (hash(f"{country_code}{year}") % 40) / 10
                    circular_score = 50.0 + (year - start_year) * 2.5
                    renewable_trade = 40.0 + (year - start_year) * 4.0
                    carbon_footprint = 65.0 + (hash(f"{country_code}{year}") % 60) / 10
                
                else:  # Other countries with varied profiles
                    carbon_intensity = 0.4 + (hash(f"{country_code}{year}") % 100) / 1000
                    green_trade_share = 20.0 + (year - start_year) * 2.0 + (hash(f"{country_code}{year}") % 100) / 10
                    transport_emissions = 30.0 + (hash(f"{country_code}{year}") % 40) / 10
                    circular_score = 40.0 + (year - start_year) * 2.0 + (hash(f"{country_code}{year}") % 100) / 10
                    renewable_trade = 30.0 + (year - start_year) * 3.0 + (hash(f"{country_code}{year}") % 100) / 10
                    carbon_footprint = 55.0 + (hash(f"{country_code}{year}") % 50) / 10
                
                environmental_data.append({
                    'country_id': country_id,
                    'year': year,
                    'carbon_intensity': carbon_intensity,
                    'green_trade_share': green_trade_share,
                    'transport_emissions': transport_emissions,
                    'circular_economy_score': circular_score,
                    'renewable_energy_trade': renewable_trade,
                    'carbon_footprint': carbon_footprint,
                    'source': 'Sample Environmental Data'
                })
        
        self._save_environmental_data(environmental_data)
        logger.info(f"Generated {len(environmental_data)} environmental records")
    
    def _save_environmental_data(self, data: List[Dict]):
        """Save environmental data to database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        for record in data:
            try:
                cursor.execute('''
                    INSERT OR REPLACE INTO environmental_metrics 
                    (country_id, year, carbon_intensity, green_trade_share, transport_emissions,
                     circular_economy_score, renewable_energy_trade, carbon_footprint, source)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    record['country_id'],
                    record['year'],
                    record['carbon_intensity'],
                    record['green_trade_share'],
                    record['transport_emissions'],
                    record['circular_economy_score'],
                    record['renewable_energy_trade'],
                    record['carbon_footprint'],
                    record['source']
                ))
            except Exception as e:
                logger.error(f"Error saving environmental data: {e}")
                continue
        
        conn.commit()
        conn.close()
    
    def _generate_sample_policy_data(self) -> List[Dict]:
        """Generate sample policy data for demonstration."""
        return [
            {
                'country_id': 1, 'policy_name': 'USMCA Implementation',
                'policy_type': 'agreement', 'description': 'US-Mexico-Canada Agreement ongoing implementation',
                'effective_date': '2021-01-01', 'status': 'active', 'source': 'USTR'
            },
            {
                'country_id': 2, 'policy_name': 'RCEP Agreement',
                'policy_type': 'agreement', 'description': 'Regional Comprehensive Economic Partnership implementation',
                'effective_date': '2022-01-01', 'status': 'active', 'source': 'WTO'
            },
            {
                'country_id': 4, 'policy_name': 'EU Green Deal',
                'policy_type': 'regulation', 'description': 'European Green Deal trade regulations',
                'effective_date': '2021-07-14', 'status': 'active', 'source': 'EU'
            },
            {
                'country_id': 4, 'policy_name': 'Carbon Border Adjustment Mechanism',
                'policy_type': 'carbon_tariff', 'description': 'EU carbon border tax on imports',
                'effective_date': '2023-10-01', 'status': 'active', 'source': 'EU'
            },
            {
                'country_id': 1, 'policy_name': 'Inflation Reduction Act',
                'policy_type': 'green_agreement', 'description': 'US green energy and trade incentives',
                'effective_date': '2022-08-16', 'status': 'active', 'source': 'US Congress'
            },
            {
                'country_id': 3, 'policy_name': 'German Circular Economy Act',
                'policy_type': 'circular_policy', 'description': 'Circular economy regulations for trade',
                'effective_date': '2021-06-01', 'status': 'active', 'source': 'German Government'
            }
        ]
    
    def _save_tariff_data(self, data: List[Dict]):
        """Save tariff data to database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        for record in data:
            cursor.execute('''
                INSERT OR REPLACE INTO tariffs 
                (country_id, partner_country_id, commodity_code, tariff_rate, 
                 tariff_type, effective_date, source)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                record['country_id'], record['partner_country_id'],
                record['commodity_code'], record['tariff_rate'],
                record['tariff_type'], record['effective_date'], record['source']
            ))
        
        conn.commit()
        conn.close()
    
    def _save_sanctions_data(self, data: List[Dict]):
        """Save sanctions data to database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        for record in data:
            cursor.execute('''
                INSERT OR REPLACE INTO sanctions 
                (sanctioning_country_id, target_country_id, sanction_type, description,
                 start_date, status, source)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                record['sanctioning_country_id'], record['target_country_id'],
                record['sanction_type'], record['description'],
                record['start_date'], record['status'], record['source']
            ))
        
        conn.commit()
        conn.close()
    
    def _save_policy_data(self, data: List[Dict]):
        """Save policy data to database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        for record in data:
            cursor.execute('''
                INSERT OR REPLACE INTO trade_policies 
                (country_id, policy_name, policy_type, description, effective_date, status, source)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                record['country_id'], record['policy_name'], record['policy_type'],
                record['description'], record['effective_date'], record['status'], record['source']
            ))
        
        conn.commit()
        conn.close()

def main():
    """Main function to run data collection."""
    
    # Create logs directory
    logs_dir = project_root / 'logs'
    logs_dir.mkdir(exist_ok=True)
    
    # Database path
    db_path = project_root / 'data' / 'sql' / 'trade_analysis.db'
    
    if not db_path.exists():
        logger.error("Database not found. Please run setup_database.py first.")
        sys.exit(1)
    
    # Initialize collector
    collector = TradeDataCollector(str(db_path))
    
    # Collect data for the last 4 years
    current_year = datetime.now().year
    start_year = current_year - 4
    
    try:
        collector.collect_all_data(start_year, current_year)
        logger.info("Data collection completed successfully!")
        
    except Exception as e:
        logger.error(f"Data collection failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 