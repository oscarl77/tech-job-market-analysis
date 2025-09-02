import pandas as pd
from datetime import datetime

from src.config import SKILL_KEYWORDS, REGION_TO_CITIES_MAP
from src.data_processing.data_cleaning import (
    parse_salary,
    classify_location_by_city,
    classify_location_by_region,
    parse_date,
    classify_by_seniority, extract_skills_from_description
)

def test_parse_salary():
    """Test that various salary formats are parsed correctly."""
    assert parse_salary("£50,000 - £60,000") == 55000
    assert parse_salary("From £30,000 to £40,000 per annum") == 35000
    assert parse_salary("70k - 80k") == 75000
    assert parse_salary("£55k per annum") == 55000
    assert parse_salary("45000") == 45000
    assert parse_salary("£500 a day") == 125000
    assert parse_salary("£450 - £550 per day") == 125000
    assert parse_salary("£50 per hour") == 100000
    assert parse_salary("£40 - 60 per hour") == 100000
    assert parse_salary("Competitive") == 0

def test_classify_location_by_city():
    """Test that locations are standardized correctly by city or otherwise"""
    assert classify_location_by_city("City Centre, Manchester (M1), M1") == "Manchester"
    assert classify_location_by_city("Greater London") == "London"
    assert classify_location_by_city("Reading") == "Other UK"
    assert classify_location_by_city("Unspecified") == "Other UK"

def test_classify_location_by_region():
    """Test that locations are standardized correctly by region."""
    assert classify_location_by_region("Greater London (Hybrid)", REGION_TO_CITIES_MAP) == "London"
    assert classify_location_by_region("Manchester, Greater Manchester", REGION_TO_CITIES_MAP) == "North West"
    assert classify_location_by_region("Oxford", REGION_TO_CITIES_MAP) == "South East"
    assert classify_location_by_region("Cheltenham, Gloucestershire", REGION_TO_CITIES_MAP) == "South West"
    assert classify_location_by_region("Unspecified", REGION_TO_CITIES_MAP) == "Other"

def test_parse_date():
    """Test that relative dates are converted correctly using a fixed 'now' date."""
    fixed_now = datetime(2025, 9, 1)
    assert parse_date("Published: 19 hours ago") == fixed_now
    assert parse_date("Published: 2 weeks ago") == datetime(2025, 8, 18)
    assert parse_date("Posted 3 days ago") == datetime(2025, 8, 29)
    assert parse_date("1 month ago") == datetime(2025, 8, 2)
    assert parse_date("N/A") is None

def test_extract_skills_from_description():
    full_descriptions = [
        # Case 1: Simple match
        "We are looking for a developer with experience in Python and SQL.",
        # Case 2: Case-insensitivity and more skills
        "Must know python, AWS, and tableau.",
        # Case 3: Whole-word matching (should not find 'R' in 'Senior')
        "Seeking a Senior Data Analyst with strong Excel skills.",
        # Case 4: No relevant skills
        "A management role requiring great communication.",
        # Case 5: Many skills
        "Experience with Docker, Kubernetes, and CI/CD is required."
    ]
    expected_skills = [
        ['Python', 'SQL'],
        ['Python', 'AWS', 'Tableau'],
        [],
        [],
        ['Docker', 'Kubernetes', 'CI/CD']
    ]
    assert extract_skills_from_description(full_descriptions[0], SKILL_KEYWORDS) == expected_skills[0]
    assert extract_skills_from_description(full_descriptions[1], SKILL_KEYWORDS) == expected_skills[1]
    assert extract_skills_from_description(full_descriptions[2], SKILL_KEYWORDS) == expected_skills[2]
    assert extract_skills_from_description(full_descriptions[3], SKILL_KEYWORDS) == expected_skills[3]
    assert extract_skills_from_description(full_descriptions[4], SKILL_KEYWORDS) == expected_skills[4]

def test_classify_seniority():
    """Test the seniority classification logic."""
    # Test title-based classification
    assert classify_by_seniority("Senior Data Engineer", "", 0) == "Senior"
    assert classify_by_seniority("Jr. Software Engineer", "", 0) == "Junior"
    assert classify_by_seniority("Lead Data Scientist", "", 0) == "Senior"

    # Test description-based classification (years of experience)
    assert classify_by_seniority("Data Analyst", "Requires 5+ years of experience", 0) == "Senior"
    assert classify_by_seniority("Data Analyst", "Looking for someone with 1 year of experience", 0) == "Junior"

    # Test salary-based classification
    assert classify_by_seniority("Data Engineer", "", 80000) == "Senior"
    assert classify_by_seniority("Data Engineer", "", 35000) == "Junior"

    # Test default case
    assert classify_by_seniority("Data Engineer", "Some description", 55000) == "Mid-Level"