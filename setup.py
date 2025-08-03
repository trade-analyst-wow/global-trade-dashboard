#!/usr/bin/env python3
"""
Setup Script for Global Trade Analysis Dashboard
Automates installation, configuration, and initial setup of the dashboard.
"""

import os
import sys
import subprocess
import platform
from pathlib import Path
import argparse

class DashboardSetup:
    """Setup class for the trade analysis dashboard."""
    
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.python_version = sys.version_info
        
    def check_prerequisites(self):
        """Check if all prerequisites are met."""
        print("🔍 Checking prerequisites...")
        
        # Check Python version
        if self.python_version < (3, 8):
            print("❌ Python 3.8 or higher is required")
            return False
        else:
            print(f"✅ Python {self.python_version.major}.{self.python_version.minor} detected")
        
        # Check if pip is available
        try:
            subprocess.run([sys.executable, "-m", "pip", "--version"], 
                         check=True, capture_output=True)
            print("✅ pip is available")
        except subprocess.CalledProcessError:
            print("❌ pip is not available")
            return False
        
        # Check if R is available (optional)
        try:
            subprocess.run(["R", "--version"], check=True, capture_output=True)
            print("✅ R is available")
            self.r_available = True
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("⚠️  R is not available (optional for advanced analysis)")
            self.r_available = False
        
        return True
    
    def create_directories(self):
        """Create necessary directories."""
        print("📁 Creating project directories...")
        
        directories = [
            "logs",
            "data/raw",
            "data/processed",
            "analysis/plots",
            "analysis/reports",
            "dashboards/powerbi",
            "dashboards/excel"
        ]
        
        for directory in directories:
            dir_path = self.project_root / directory
            dir_path.mkdir(parents=True, exist_ok=True)
            print(f"✅ Created {directory}")
    
    def install_python_dependencies(self):
        """Install Python dependencies."""
        print("🐍 Installing Python dependencies...")
        
        requirements_file = self.project_root / "requirements" / "python_requirements.txt"
        
        if not requirements_file.exists():
            print("❌ Python requirements file not found")
            return False
        
        try:
            subprocess.run([
                sys.executable, "-m", "pip", "install", "-r", str(requirements_file)
            ], check=True)
            print("✅ Python dependencies installed successfully")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install Python dependencies: {e}")
            return False
    
    def install_r_dependencies(self):
        """Install R dependencies."""
        if not self.r_available:
            print("⚠️  Skipping R dependencies (R not available)")
            return True
        
        print("📊 Installing R dependencies...")
        
        r_requirements_file = self.project_root / "requirements" / "r_requirements.R"
        
        if not r_requirements_file.exists():
            print("❌ R requirements file not found")
            return False
        
        try:
            subprocess.run(["Rscript", str(r_requirements_file)], check=True)
            print("✅ R dependencies installed successfully")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install R dependencies: {e}")
            return False
    
    def setup_database(self):
        """Set up the database."""
        print("🗄️  Setting up database...")
        
        setup_script = self.project_root / "src" / "sql" / "setup_database.py"
        
        if not setup_script.exists():
            print("❌ Database setup script not found")
            return False
        
        try:
            subprocess.run([sys.executable, str(setup_script)], check=True)
            print("✅ Database setup completed successfully")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to setup database: {e}")
            return False
    
    def create_env_file(self):
        """Create environment configuration file."""
        print("⚙️  Creating environment configuration...")
        
        env_file = self.project_root / ".env"
        env_example = self.project_root / ".env.example"
        
        if env_file.exists():
            print("✅ Environment file already exists")
            return True
        
        # Create .env.example if it doesn't exist
        if not env_example.exists():
            env_content = """# API Keys for Data Sources
# Get these from the respective organizations

# World Bank API (optional - for enhanced data)
WORLD_BANK_API_KEY=your_world_bank_api_key_here

# IMF API (optional - for enhanced data)
IMF_API_KEY=your_imf_api_key_here

# OECD API (optional - for enhanced data)
OECD_API_KEY=your_oecd_api_key_here

# Database Configuration
DATABASE_URL=sqlite:///data/sql/trade_analysis.db

# Logging Configuration
LOG_LEVEL=INFO
LOG_FILE=logs/dashboard.log

# Dashboard Configuration
DASHBOARD_HOST=localhost
DASHBOARD_PORT=8501
"""
            with open(env_example, 'w') as f:
                f.write(env_content)
        
        # Copy .env.example to .env
        try:
            with open(env_example, 'r') as src, open(env_file, 'w') as dst:
                dst.write(src.read())
            print("✅ Environment file created (update with your API keys)")
            return True
        except Exception as e:
            print(f"❌ Failed to create environment file: {e}")
            return False
    
    def collect_sample_data(self):
        """Collect sample data for demonstration."""
        print("📊 Collecting sample data...")
        
        collector_script = self.project_root / "src" / "python" / "data_collector.py"
        
        if not collector_script.exists():
            print("❌ Data collector script not found")
            return False
        
        try:
            subprocess.run([sys.executable, str(collector_script)], check=True)
            print("✅ Sample data collection completed")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to collect sample data: {e}")
            return False
    
    def generate_excel_template(self):
        """Generate Excel template."""
        print("📈 Generating Excel template...")
        
        template_script = self.project_root / "dashboards" / "excel" / "trade_analysis_template.py"
        
        if not template_script.exists():
            print("❌ Excel template script not found")
            return False
        
        try:
            subprocess.run([sys.executable, str(template_script)], check=True)
            print("✅ Excel template generated successfully")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to generate Excel template: {e}")
            return False
    
    def run_analysis(self):
        """Run initial analysis."""
        if not self.r_available:
            print("⚠️  Skipping R analysis (R not available)")
            return True
        
        print("📊 Running initial analysis...")
        
        analysis_script = self.project_root / "src" / "r" / "analysis_script.R"
        
        if not analysis_script.exists():
            print("❌ Analysis script not found")
            return False
        
        try:
            subprocess.run(["Rscript", str(analysis_script)], check=True)
            print("✅ Initial analysis completed")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to run analysis: {e}")
            return False
    
    def create_startup_scripts(self):
        """Create startup scripts for easy access."""
        print("🚀 Creating startup scripts...")
        
        # Create startup script for Streamlit dashboard
        startup_script = self.project_root / "start_dashboard.py"
        startup_content = '''#!/usr/bin/env python3
"""
Startup script for the Trade Analysis Dashboard
"""

import subprocess
import sys
from pathlib import Path

def main():
    """Start the Streamlit dashboard."""
    dashboard_script = Path(__file__).parent / "src" / "python" / "dashboard_app.py"
    
    if not dashboard_script.exists():
        print("❌ Dashboard script not found")
        sys.exit(1)
    
    print("🌍 Starting Trade Analysis Dashboard...")
    print("📱 Dashboard will be available at: http://localhost:8501")
    print("🛑 Press Ctrl+C to stop the dashboard")
    
    try:
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", str(dashboard_script)
        ])
    except KeyboardInterrupt:
        print("\\n👋 Dashboard stopped")

if __name__ == "__main__":
    main()
'''
        
        with open(startup_script, 'w') as f:
            f.write(startup_content)
        
        # Make executable on Unix systems
        if platform.system() != "Windows":
            os.chmod(startup_script, 0o755)
        
        print("✅ Startup script created: start_dashboard.py")
    
    def print_next_steps(self):
        """Print next steps for the user."""
        print("\n" + "="*60)
        print("🎉 SETUP COMPLETED SUCCESSFULLY!")
        print("="*60)
        
        print("\n📋 Next Steps:")
        print("1. Update API keys in .env file (optional)")
        print("2. Start the dashboard: python start_dashboard.py")
        print("3. Open your browser to: http://localhost:8501")
        
        print("\n📚 Documentation:")
        print("- Project overview: README.md")
        print("- Detailed documentation: docs/project_documentation.md")
        
        print("\n🔧 Available Commands:")
        print("- Start dashboard: python start_dashboard.py")
        print("- Collect data: python src/python/data_collector.py")
        print("- Run analysis: Rscript src/r/analysis_script.R")
        print("- Generate Excel: python dashboards/excel/trade_analysis_template.py")
        
        print("\n📁 Project Structure:")
        print("- src/python/: Python scripts")
        print("- src/r/: R analysis scripts")
        print("- src/sql/: Database scripts")
        print("- dashboards/: Dashboard files")
        print("- analysis/: Analysis outputs")
        print("- data/: Data files")
        
        print("\n💡 Tips:")
        print("- The dashboard includes sample data for demonstration")
        print("- Add your own API keys for enhanced data collection")
        print("- Customize analysis parameters in the scripts")
        print("- Check logs/ directory for detailed logs")
        
        print("\n" + "="*60)
    
    def run_full_setup(self):
        """Run the complete setup process."""
        print("🚀 Starting Global Trade Analysis Dashboard Setup")
        print("="*60)
        
        # Check prerequisites
        if not self.check_prerequisites():
            print("❌ Prerequisites not met. Please install required software.")
            return False
        
        # Create directories
        self.create_directories()
        
        # Install dependencies
        if not self.install_python_dependencies():
            return False
        
        if not self.install_r_dependencies():
            return False
        
        # Setup database
        if not self.setup_database():
            return False
        
        # Create environment file
        if not self.create_env_file():
            return False
        
        # Collect sample data
        if not self.collect_sample_data():
            return False
        
        # Generate Excel template
        if not self.generate_excel_template():
            return False
        
        # Run analysis
        if not self.run_analysis():
            return False
        
        # Create startup scripts
        self.create_startup_scripts()
        
        # Print next steps
        self.print_next_steps()
        
        return True

def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="Setup Global Trade Analysis Dashboard")
    parser.add_argument("--skip-data", action="store_true", 
                       help="Skip data collection step")
    parser.add_argument("--skip-analysis", action="store_true", 
                       help="Skip analysis step")
    parser.add_argument("--skip-excel", action="store_true", 
                       help="Skip Excel template generation")
    
    args = parser.parse_args()
    
    setup = DashboardSetup()
    
    try:
        success = setup.run_full_setup()
        if success:
            print("\n✅ Setup completed successfully!")
            sys.exit(0)
        else:
            print("\n❌ Setup failed. Please check the errors above.")
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Setup interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error during setup: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 