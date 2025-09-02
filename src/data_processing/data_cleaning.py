import re
import pandas as pd
from sqlalchemy import create_engine, inspect
from datetime import datetime, timedelta

def load_raw_data(db_path, table_name):
    """
    Load the raw data from the database into a DataFrame.
    :param db_path: Path to the SQLite database.
    :param table_name: Name of the table to load.
    :return: A DataFrame containing the raw data, or an empty one on error.
    """
    engine = create_engine(f'sqlite:///{db_path}')
    inspector = inspect(engine)
    if not inspector.has_table(table_name):
        return pd.DataFrame()
    df = pd.read_sql_table(table_name, engine)
    print(f"Successfully loaded {len(df)} rows.")
    return df

def classify_location_by_city(location_string):
    """
    Standardize a messy location string into a primary city or "Other UK"
    :param location_string: Raw location string.
    :return: A primary city if it is in the string, otherwise "Other UK"
    """
    if not isinstance(location_string, str):
        return "N/A"
    location_lower = location_string.lower()
    target_cities = [
        'London', 'Manchester', 'Birmingham', 'Bristol', 'Leeds',
        'Glasgow', 'Edinburgh', 'Cambridge', 'Oxford', 'Cardiff', 'Belfast'
    ]
    for city in target_cities:
        if city.lower() in location_lower:
            return city
    return "Other UK"

def classify_location_by_region(location_string, region_to_cities_map):
    """
        Standardize a messy location string into a region.
        :param location_string: Raw location string.
        :param region_to_cities_map: Dictionary of region to list of cities.
        :return: The region that the location string refers to.
        """
    location_lower = location_string.lower()
    for region, cities in region_to_cities_map.items():
        for city in cities:
            if city.lower() in location_lower:
                return region
    return "Other"

def categorize_employment_type(employment_type):
    """
    Categorize employment type based on the employment type.
    :param employment_type: Raw employment type.
    :return: Unchanged if Permanent or Contract, otherwise grouped into
    one of the two.
    """
    mapping = {
        "Temporary": "Contract",
        "Not Assigned": "Permanent"
    }
    if employment_type in mapping:
        return mapping[employment_type]
    return employment_type

def parse_date(date_string):
    """
    Convert relative date string (e.g '2 weeks ago') to 'dd/mm/yyyy' format.
    :param date_string: Relative date string.
    :return: Date in 'dd/mm/yyyy' format, or None if string could not be parsed.
    """
    if not isinstance(date_string, str):
        return None
    date_string = date_string.lower()
    scrape_date = datetime(2025, 9, 1)
    if 'hour' in date_string:
        past_date = scrape_date
    else:
        match = re.search(r'(\d+)', date_string)
        if match:
            num = int(match.group(1))
            if 'week' in date_string:
                delta = timedelta(weeks=num)
            elif 'day' in date_string:
                delta = timedelta(days=num)
            elif 'month' in date_string:
                # timedelta doesn't have a 'months' argument, so approximate
                delta = timedelta(days=num * 30)
            else:
                return None
            past_date = scrape_date - delta
        else:
            return None
    return past_date

def parse_salary(salary_string):
    """
    Parse raw salary string into numerical values.
    :param salary_string: Raw salary string.
    :return: Yearly salary as a numerical value.
    """
    if not isinstance(salary_string, str):
        return 0
    salary_lower = salary_string.lower()
    if 'competitive' in salary_lower:
        return 0
    salary_clean = salary_lower.replace('£', '').replace(',', '').replace('k', '000')
    numbers = [int(n) for n in re.findall(r'\d+', salary_clean)]
    if not numbers:
        return 0
    if 'hour' in salary_lower:
        if len(numbers) > 1:
            avg_hourly_rate = (numbers[0] + numbers[-1]) / len(numbers)
        else:
            avg_hourly_rate = numbers[0]
        return int(avg_hourly_rate * 8 * 250)
    if 'day' in salary_lower or 'daily' in salary_lower:
        if len(numbers) >= 2:
            avg_daily_rate = (numbers[0] + numbers[1]) / 2
            return int(avg_daily_rate * 250)
        else:
            return int(numbers[0] * 250)
    else:
        if len(numbers) >= 2:
            return int((numbers[0] + numbers[1]) / 2)
        else:
            return int(numbers[0])

def extract_skills_from_description(job_description, skill_keywords):
    """
    Extract skills from job description.
    :param job_description: Full job description.
    :param skill_keywords: List of keywords to extract.
    :return: List of skills found.
    """
    found_skills = []
    description_lower = str(job_description).lower()
    for skill in skill_keywords:
        # Use word boundaries (\b) in regex to avoid matching substrings
        if re.search(r'\b' + re.escape(skill.lower()) + r'\b', description_lower):
            found_skills.append(skill)
    return found_skills

def classify_by_seniority(title, description, salary=0):
    """
    Classify job seniority based on keywords in the title, description, and salary.
    :param title: Job title.
    :param description: Job description.
    :param salary: Salary for the role.
    :return: 'Senior', 'Mid-Level', or 'Junior' strings.
    """
    title_lower = str(title).lower()
    description_lower = str(description).lower()
    senior_keywords = ['senior', 'sr', 'lead', 'principal', 'manager', 'head of']
    junior_keywords = ['junior', 'jr', 'entry', 'graduate', 'trainee', 'intern']
    if any(keyword in title_lower for keyword in senior_keywords):
        return 'Senior'
    if any(keyword in title_lower for keyword in junior_keywords):
        return 'Junior'
    # Check for quantitative experience (e.g., "5+ years")
    experience_match = re.search(r'(\d+)\+?\s*years?', description_lower)
    if experience_match:
        years = int(experience_match.group(1))
        if years >= 5:
            return 'Senior'
        if years <= 2:
            return 'Junior'
    senior_desc_keywords = ['strong experience', 'extensive experience', 'deep understanding']
    if any(keyword in description_lower for keyword in senior_desc_keywords):
        return 'Senior'
    if salary >= 70000:
        return 'Senior'
    if 0 < salary <= 40000:
        return 'Junior'
    return 'Mid-Level'

if __name__ == '__main__':
    print(parse_salary("£50 per hour"))