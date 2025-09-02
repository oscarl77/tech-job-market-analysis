import re
from datetime import datetime, timedelta
from src.config import DB_PATH, RAW_DATA_TABLE_NAME, PROCESSED_DATA_TABLE_NAME, REGION_TO_CITIES_MAP, SKILL_KEYWORDS
from src.utils import save_data_to_db, load_data_from_db


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
    return past_date.date()

def parse_salary(salary_string):
    """
        Parse raw salary string into numerical values.
        :param salary_string: Raw salary string.
        :return: Yearly salary as a numerical value.
        """
    if not isinstance(salary_string, str):
        return 0
    salary_lower = salary_string.lower()
    if any(keyword in salary_lower for keyword in ['competitive', 'market rate']):
        return 0
    salary_no_commas = salary_lower.replace(',', '')
    # This regex finds integers and decimals (e.g., '50', '42.5')
    numbers_str = re.findall(r'(\d+\.?\d*)', salary_no_commas)
    if not numbers_str:
        return 0
    numbers = [float(n) for n in numbers_str]
    # Apply 'k' multiplier if present in the original string
    if re.search(r'\d+k', salary_lower):
        numbers = [n * 1000 for n in numbers]
    avg_rate = sum(numbers) / len(numbers)
    if 'hour' in salary_lower:
        return int(avg_rate) if avg_rate > 200 else int(avg_rate * 8 * 250)
    if 'day' in salary_lower:
        return int(avg_rate) if avg_rate > 2000 else int(avg_rate * 250)
    if 100 < avg_rate < 1000:
        return int(avg_rate * 250)
    if avg_rate < 100:
        int(avg_rate * 8 * 250)
    return int(avg_rate)

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

def classify_by_seniority(row):
    title = row['job_title']
    description = row['full_description']
    salary = row['salary_numeric']

    return _classify_seniority(title, description, salary)

def _classify_seniority(title, description, salary=0):
    """
    Classify job seniority based on keywords in the title, description, and salary.
    :param title: Job title.
    :param description: Job description.
    :param salary: Salary for the role.
    :return: 'Senior', 'Mid-Level', or 'Junior' strings.
    """
    title_lower = str(title).lower()
    description_lower = str(description).lower()
    senior_keywords = ['senior', 'sr', 'manager', 'head of']
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
    df = load_data_from_db(DB_PATH, RAW_DATA_TABLE_NAME)
    df['salary_numeric'] = df['salary_raw'].apply(parse_salary)
    df['seniority'] = df.apply(classify_by_seniority, axis=1)
    df['city'] = df['location'].apply(classify_location_by_city)
    df['region'] = df['location'].apply(lambda x: classify_location_by_region(x, REGION_TO_CITIES_MAP))
    df['employment_type_clean'] = df['employment_type'].apply(categorize_employment_type)
    df['date_posted'] = df['date_posted_raw'].apply(parse_date)
    df['skills'] = df['full_description'].apply(lambda x: extract_skills_from_description(x, SKILL_KEYWORDS))
    df['skills'] = df['skills'].apply(lambda x: ','.join(x) if isinstance(x, list) else '')
    columns_to_keep = [
        'search_category', 'job_title', 'company_name', 'seniority', 'salary_numeric', 'employment_type_clean',
        'city', 'region', 'date_posted','skills'
    ]
    final_columns = [col for col in columns_to_keep if col in df.columns]
    final_df = df[final_columns]
    save_data_to_db(final_df, PROCESSED_DATA_TABLE_NAME, DB_PATH)


