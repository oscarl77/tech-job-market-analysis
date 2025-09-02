from pathlib import Path

BASE_URL = "https://www.cwjobs.co.uk/jobs/"
JOB_POST_BASE_URL = "https://www.cwjobs.co.uk"
URL_TAIL = "?page={page_number}&searchOrigin=jobad"
ARTICLE_CLASS = "a.res-30nsen"
JOB_TITLE = "DevOps Engineer"
PAGES_TO_SCRAPE = 11

current_file_path = Path(__file__).resolve()
BASE_DIR = current_file_path.parent.parent
DB_PATH = BASE_DIR / 'jobs.db'

RAW_DATA_TABLE_NAME = 'jobs_raw'
PROCESSED_DATA_TABLE_NAME = 'jobs_processed'

REGION_TO_CITIES_MAP = {
        'North': [
            # North West
            'North West', 'Manchester', 'Rochdale', 'Blackburn', 'Warrington', 'Liverpool', 'Wigan', 'Stockport', 'Ormskirk', 'Salford', 'Blackburn', 'Cheshire', 'Merseyside', 'Preston',
            # Yorkshire
            'Yorkshire', 'North East' ,'Lancashire', 'Leeds', 'Bradford', 'Huddersfield', 'Newcastle', 'Sheffield', 'Beverly', 'Doncaster', 'Hartlepool', 'Grimsby', 'Ripon', 'Lincolnshire',
            # Midlands
            'Midlands', 'Leicestershire', 'Birmingham','Worcestershire', 'Warwickshire', 'Derby', 'Hinckley', 'Shropshire', 'Coventry', 'Leicester', 'Warwick', 'Nottingham', 'Burton-On-Trent', 'Solihull', 'Markfield', 'Hereford'
        ],
        'South': [
            # South East
            'South East', 'Oxford', 'Oxfordshire', 'Aldershot', 'Stevenage', 'Berkshire', 'Hampshire', 'Bexhill-On_Sea', 'Newbury', 'Reading', 'Sandhurst', 'Maidenhead', 'Sussex', 'Surrey', 'Dartford', 'Slough', 'Fareham', 'Guildford', 'Maidstone', 'Aylesbury', 'Wallingford', 'Chesham', 'Milton Keynes', 'Kent', 'Margate',
            # South West
            'South West', 'Gloucester', 'Devon', 'Bristol', 'Dorset', 'Cheltenham', 'Plymouth', 'Cornwall', 'Dorchester', 'Exeter', 'Chippenham',
            # East of England
            'East of England', 'Hertfordshire', 'Bedfordshire', 'Cambridge','East Anglia', 'Norwich', 'Bedford', 'Suffolk', 'Norfolk', 'Basildon'
        ],
        'London': ['London', 'Croydon', 'Hounslow'],
        # Other, including Scotland, Wales and Ireland
        'Other': ['UK', 'Unspecified', 'Ireland', 'Belfast', 'Scotland', 'Glasgow', 'Edinburgh', 'Aberdeen', 'Wales', 'Swansea', 'Cardiff', 'Bridgend']
    }

SKILL_KEYWORDS = [
    # Programming & Scripting Languages
    'Python', 'Java', 'C#', 'C++', 'JavaScript', 'TypeScript', 'SQL',
    'R', 'Scala', 'Go', 'Ruby', 'PHP',
    # Data Science & Machine Learning
    'PyTorch', 'TensorFlow', 'Scikit-learn', 'Keras', 'Pandas', 'NumPy',
    'Matplotlib', 'Seaborn', 'SciPy',
    # Data Engineering & Big Data
    'Spark', 'PySpark', 'Hadoop', 'Kafka', 'Airflow', 'Databricks',
    'Informatica', 'ETL',
    # Databases & Data Warehouses
    'PostgreSQL', 'MySQL', 'SQL Server', 'MongoDB', 'Cassandra', 'Redis',
    'Snowflake', 'Redshift', 'BigQuery', 'DynamoDB', 'Elasticsearch',
    # Cloud Platforms & Services
    'AWS', 'Azure', 'GCP', 'S3', 'EC2', 'Lambda', 'Glue', 'EMR',
    'Azure Functions', 'Synapse Analytics',
    # DevOps & CI/CD
    'Docker', 'Kubernetes', 'Terraform', 'Jenkins', 'Git', 'CI/CD',
    'Ansible', 'GitLab', 'GitHub Actions',
    # BI & Visualization
    'Tableau', 'Power BI', 'Qlik', 'Looker', 'SSIS',
    # Web Development (Frontend)
    'React', 'Vue', 'Angular'
]
