"""
Resume Parser Module
Extracts information from resume files (PDF, DOC, DOCX)
"""
import re
from pathlib import Path
from typing import Dict, List, Optional
import PyPDF2


def parse_resume(file_path: str) -> Dict:
    """
    Parse resume file and extract structured information.
    
    Args:
        file_path: Path to resume file (PDF, DOC, DOCX)
    
    Returns:
        Dictionary containing extracted information
    """
    file_path = Path(file_path)
    
    if file_path.suffix.lower() == '.pdf':
        text = extract_text_from_pdf(file_path)
    elif file_path.suffix.lower() in ['.doc', '.docx']:
        text = extract_text_from_docx(file_path)
    else:
        raise ValueError(f"Unsupported file format: {file_path.suffix}")
    
    return extract_resume_data(text)


def extract_text_from_pdf(file_path: Path) -> str:
    """Extract text from PDF file."""
    text = ""
    try:
        with open(file_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            for page in reader.pages:
                text += page.extract_text() + "\n"
    except Exception as e:
        print(f"Error extracting text from PDF: {e}")
    return text


def extract_text_from_docx(file_path: Path) -> str:
    """Extract text from DOCX file."""
    try:
        from docx import Document
        doc = Document(file_path)
        text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
        return text
    except ImportError:
        print("python-docx not installed. Install with: pip install python-docx")
        return ""
    except Exception as e:
        print(f"Error extracting text from DOCX: {e}")
        return ""


def extract_resume_data(text: str) -> Dict:
    """
    Extract structured data from resume text.

    Returns dictionary with:
    - full_name
    - email
    - phone
    - location
    - linkedin
    - github
    - portfolio
    - education
    - skills
    - experience
    - certifications
    - target_roles (extracted from job titles)
    """
    experience_data = extract_experience(text)

    data = {
        'full_name': extract_name(text),
        'email': extract_email(text),
        'phone': extract_phone(text),
        'location': extract_location(text),
        'linkedin': extract_linkedin(text),
        'github': extract_github(text),
        'portfolio': extract_portfolio(text),
        'education': extract_education(text),
        'skills': extract_skills(text),
        'experience': experience_data,
        'certifications': extract_certifications(text),
        'target_roles': experience_data.get('job_titles', []),
    }

    return data


def extract_name(text: str) -> Optional[str]:
    """Extract full name from resume."""
    # Look for name at the beginning of the document
    lines = text.split('\n')
    for line in lines[:5]:
        line = line.strip()
        if line and len(line.split()) >= 2 and len(line) < 50:
            # Check if it looks like a name (capitalized words)
            words = line.split()
            if all(word[0].isupper() if word else False for word in words[:3]):
                return line
    return None


def extract_email(text: str) -> Optional[str]:
    """Extract email address."""
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    match = re.search(email_pattern, text)
    return match.group(0) if match else None


def extract_phone(text: str) -> Optional[str]:
    """Extract phone number."""
    # Match Indian phone numbers
    phone_patterns = [
        r'\+91[-\s]?\d{10}',
        r'\d{10}',
        r'\(?\d{3}\)?[-\s]?\d{3}[-\s]?\d{4}',
    ]
    
    for pattern in phone_patterns:
        match = re.search(pattern, text)
        if match:
            return match.group(0)
    return None


def extract_location(text: str) -> Optional[str]:
    """Extract location/city."""
    # Common Indian cities
    cities = [
        'Bangalore', 'Bengaluru', 'Mumbai', 'Delhi', 'Hyderabad', 'Chennai',
        'Pune', 'Kolkata', 'Ahmedabad', 'Jaipur', 'Lucknow', 'Chandigarh',
        'Gurgaon', 'Noida', 'Ghaziabad', 'Faridabad', 'Nagpur', 'Indore'
    ]
    
    for city in cities:
        if city.lower() in text.lower():
            return city
    
    return None


def extract_linkedin(text: str) -> Optional[str]:
    """Extract LinkedIn profile URL."""
    linkedin_pattern = r'linkedin\.com/in/[A-Za-z0-9-]+'
    match = re.search(linkedin_pattern, text, re.IGNORECASE)
    return f"https://{match.group(0)}" if match else None


def extract_github(text: str) -> Optional[str]:
    """Extract GitHub profile URL."""
    github_pattern = r'github\.com/[A-Za-z0-9_-]+'
    match = re.search(github_pattern, text, re.IGNORECASE)
    return f"https://{match.group(0)}" if match else None


def extract_portfolio(text: str) -> Optional[str]:
    """Extract portfolio website URL."""
    url_pattern = r'https?://[^\s<>"]+|www\.[^\s<>"]+'
    urls = re.findall(url_pattern, text)
    
    # Filter out LinkedIn and GitHub
    for url in urls:
        if 'linkedin' not in url.lower() and 'github' not in url.lower():
            return url if url.startswith('http') else f"https://{url}"
    
    return None


def extract_education(text: str) -> Dict:
    """Extract education information."""
    education = {
        'degree': None,
        'university': None,
        'year': None,
        'field': None
    }
    
    # Common degree patterns
    degree_patterns = [
        r'(B\.Tech|B\.E\.|Bachelor of Technology|Bachelor of Engineering)',
        r'(M\.Tech|M\.E\.|Master of Technology|Master of Engineering)',
        r'(B\.Sc\.|Bachelor of Science)',
        r'(M\.Sc\.|Master of Science)',
        r'(Ph\.D\.|Doctor of Philosophy)',
    ]
    
    for pattern in degree_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            education['degree'] = match.group(1)
            break
    
    # Extract year
    year_pattern = r'(20\d{2})'
    years = re.findall(year_pattern, text)
    if years:
        education['year'] = years[-1]  # Most recent year
    
    # Extract university (simplified)
    university_keywords = ['University', 'Institute', 'College', 'School']
    for keyword in university_keywords:
        if keyword in text:
            # Try to extract university name
            idx = text.find(keyword)
            if idx != -1:
                context = text[max(0, idx-20):idx+50]
                education['university'] = context.strip()
                break
    
    return education


def extract_skills(text: str) -> List[str]:
    """Extract skills from resume with enhanced patterns."""
    # Comprehensive tech keywords with categories
    tech_keywords = {
        'frontend': [
            'javascript', 'typescript', 'react', 'angular', 'vue', 'svelte', 'next.js', 'nuxt.js',
            'html', 'css', 'sass', 'scss', 'less', 'tailwind', 'bootstrap', 'material-ui',
            'jquery', 'webpack', 'vite', 'parcel', 'babel', 'redux', 'mobx', 'zustand',
            'graphql', 'rest api', 'fetch', 'axios', 'd3.js', 'chart.js', 'three.js',
            'webpack', 'vite', 'jest', 'cypress', 'playwright', 'selenium'
        ],
        'backend': [
            'python', 'java', 'node', 'node.js', 'express', 'django', 'flask', 'fastapi',
            'spring', 'spring boot', 'hibernate', 'golang', 'go', 'ruby', 'rails', 'php',
            'laravel', '.net', 'c#', 'asp.net', 'asp.net core', 'rust', 'actix-web',
            'sql', 'nosql', 'mongodb', 'postgresql', 'mysql', 'sqlite', 'redis', 'elasticsearch',
            'kafka', 'rabbitmq', 'graphql', 'grpc', 'rest', 'soap', 'microservices',
            'docker', 'kubernetes', 'terraform', 'ansible', 'jenkins', 'ci/cd', 'git',
            'linux', 'ubuntu', 'windows server', 'nginx', 'apache', 'iis'
        ],
        'data': [
            'python', 'r', 'sql', 'nosql', 'mongodb', 'postgresql', 'mysql', 'sqlite',
            'pandas', 'numpy', 'scipy', 'matplotlib', 'seaborn', 'plotly', 'd3.js',
            'tableau', 'power bi', 'excel', 'excel vba', 'spark', 'hadoop', 'hive',
            'airflow', 'dbt', 'snowflake', 'redshift', 'bigquery', 'athena',
            'machine learning', 'ml', 'deep learning', 'ai', 'artificial intelligence',
            'tensorflow', 'pytorch', 'keras', 'scikit-learn', 'nlp', 'natural language processing',
            'computer vision', 'data science', 'data analysis', 'data engineering',
            'etl', 'data warehouse', 'data pipeline', 'bi', 'business intelligence'
        ],
        'devops': [
            'docker', 'kubernetes', 'k8s', 'helm', 'jenkins', 'gitlab ci', 'github actions',
            'circleci', 'travis ci', 'bamboo', 'ansible', 'chef', 'puppet', 'saltstack',
            'terraform', 'aws', 'azure', 'gcp', 'google cloud', 'azure devops',
            'linux', 'bash', 'shell scripting', 'python scripting', 'powershell',
            'ci/cd', 'continuous integration', 'continuous deployment', 'devops',
            'infrastructure as code', 'iac', 'monitoring', 'logging', 'elk stack',
            'prometheus', 'grafana', 'nagios', 'splunk', 'new relic', 'datadog'
        ],
        'cloud': [
            'aws', 'amazon web services', 'azure', 'microsoft azure', 'gcp', 'google cloud platform',
            'ec2', 's3', 'lambda', 'functions', 'app service', 'cloud functions',
            'iam', 'vpc', 'route 53', 'cloudfront', 'load balancer', 'auto scaling',
            'eks', 'aks', 'gke', 'ecs', 'fargate', 'lambda', 'cloud run', 'app engine',
            'serverless', 'containers', 'microservices', 'kubernetes', 'docker'
        ],
        'tools': [
            'git', 'github', 'gitlab', 'bitbucket', 'svn', 'mercurial',
            'jira', 'confluence', 'trello', 'asana', 'notion', 'slack', 'teams',
            'vscode', 'intellij', 'pycharm', 'webstorm', 'visual studio',
            'postman', 'soapui', 'chrome devtools', 'firefox devtools',
            'fiddler', 'charles', 'wireshark', 'tcpdump'
        ]
    }
    
    found_skills = []
    text_lower = text.lower()
    
    # Extract skills from all categories
    for category, keywords in tech_keywords.items():
        for keyword in keywords:
            if keyword in text_lower:
                # Capitalize properly
                skill = keyword.replace('.js', '.JS').replace('api', 'API')
                if skill not in found_skills:
                    found_skills.append(skill)
    
    # Also look for common patterns like "Proficient in X", "Experience with Y"
    proficiency_patterns = [
        r'(?:proficient|experienced|skilled|knowledge|familiar|expert(?:ise) in?)\s+([a-z]+(?:\s+[a-z]+)?)',
        r'(?:worked|used|utilized|implemented|developed|built|created)\s+(?:with|using|on)\s+([a-z]+(?:\s+[a-z]+)?)',
    ]
    
    for pattern in proficiency_patterns:
        matches = re.finditer(pattern, text, re.IGNORECASE)
        for match in matches:
            skill = match.group(1).strip()
            # Convert to title case
            skill = ' '.join(word.capitalize() for word in skill.split())
            if skill and skill not in found_skills:
                found_skills.append(skill)
    
    return found_skills


def extract_experience(text: str) -> Dict:
    """Extract work experience information."""
    experience = {
        'total_years': 0,
        'companies': [],
        'job_titles': []
    }

    # Extract experience duration
    exp_pattern = r'(\d+)\s*(?:years?|yrs?)\s*(?:of)?\s*experience'
    match = re.search(exp_pattern, text, re.IGNORECASE)
    if match:
        experience['total_years'] = int(match.group(1))

    # Extract companies (simplified - looks for common company indicators)
    # This is a basic implementation and may need refinement
    company_keywords = ['Inc', 'Ltd', 'LLC', 'Pvt', 'Technologies', 'Solutions', 'Systems']
    for keyword in company_keywords:
        if keyword in text:
            # Try to extract company name
            idx = text.find(keyword)
            if idx != -1:
                context = text[max(0, idx-30):idx+10]
                company = context.strip()
                if company not in experience['companies']:
                    experience['companies'].append(company)

    # Extract job titles - more comprehensive patterns
    job_title_patterns = [
        r'(?:Senior|Lead|Principal|Staff)?\s*(?:Software|Full Stack|Frontend|Backend|Web|Mobile|DevOps|Data|Machine Learning|AI)?\s*(?:Developer|Engineer)',
        r'(?:Product|Project|Technical|Engineering)\s*Manager',
        r'(?:Software|System|Cloud|Data|Solutions)\s*Architect',
        r'(?:Senior|Lead)?\s*(?:Data|Business|System)\s*Analyst',
        r'(?:UI|UX|Product|Graphic)\s*Designer',
        r'(?:Quality Assurance|QA)\s*Engineer',
        r'(?:DevOps|Site Reliability)\s*Engineer',
        r'(?:Database|Backend)\s*Developer',
        r'(?:Frontend|Web)\s*Developer',
        r'(?:Mobile|iOS|Android)\s*Developer',
    ]

    for pattern in job_title_patterns:
        matches = re.finditer(pattern, text, re.IGNORECASE)
        for match in matches:
            title = match.group(0).strip()
            # Clean up and normalize
            title = title.replace('\n', ' ').strip()
            if title and title not in experience['job_titles']:
                experience['job_titles'].append(title)

    # Also look for common role keywords separately as fallback
    title_keywords = [
        'Developer', 'Engineer', 'Manager', 'Analyst', 'Designer',
        'Architect', 'Consultant', 'Director', 'Lead', 'Senior'
    ]
    for keyword in title_keywords:
        if keyword in text:
            idx = text.find(keyword)
            if idx != -1:
                context = text[max(0, idx-20):idx+10]
                title = context.strip()
                # Only add if not already captured by patterns
                if title and not any(kw in title for kw in experience['job_titles']):
                    if title not in experience['job_titles']:
                        experience['job_titles'].append(title)

    # Map extracted job titles to standard target roles
    standard_target_roles = [
        'Full Stack Developer',
        'MERN Stack Developer',
        'React Developer',
        'Node.js Developer',
        'Frontend Developer',
        'Software Developer',
        'Software Engineer',
        'Web Developer',
        'Junior Software Developer',
        'Junior Software Engineer',
        'Junior Full Stack Developer',
        'Associate Software Engineer',
        'Associate Developer',
        'Graduate Software Engineer',
        'Trainee Software Engineer',
        'Software Engineer Trainee',
        'Frontend Engineer',
        'React.js Developer',
        'JavaScript Developer',
        'Backend Developer'
    ]

    # Try to match extracted titles to standard roles
    matched_roles = []
    for extracted_title in experience['job_titles']:
        title_lower = extracted_title.lower()
        for standard_role in standard_target_roles:
            # Check if the standard role keywords are in the extracted title
            # or if the extracted title keywords are in the standard role
            role_lower = standard_role.lower()
            if (any(word in title_lower for word in role_lower.split()) or
                any(word in role_lower for word in title_lower.split())):
                if standard_role not in matched_roles:
                    matched_roles.append(standard_role)

    # Replace job_titles with matched standard roles
    if matched_roles:
        experience['job_titles'] = matched_roles

    return experience


def extract_certifications(text: str) -> List[str]:
    """Extract certifications."""
    certification_keywords = [
        'AWS', 'Azure', 'Google Cloud', 'Certified', 'PMP',
        'Scrum', 'Agile', 'CCNA', 'Oracle', 'Microsoft'
    ]
    
    found_certs = []
    text_lower = text.lower()
    
    for keyword in certification_keywords:
        if keyword.lower() in text_lower:
            found_certs.append(keyword)
    
    return found_certs
