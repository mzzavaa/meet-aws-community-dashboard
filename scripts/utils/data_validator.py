"""
Data validation utility for AWS Community Dashboard
"""

import pandas as pd
from typing import List, Dict, Any, Tuple
from .logger import get_logger


class DataValidator:
    """Data validation and quality checks"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = get_logger("data_validator")
        
        # Validation rules from config
        self.required_fields = config.get('validation', {}).get('required_fields', {})
        self.min_records = config.get('validation', {}).get('min_records', {})
    
    def validate_dataframe(self, df: pd.DataFrame, data_type: str) -> Tuple[bool, List[str]]:
        """
        Validate a DataFrame against configured rules
        
        Args:
            df: DataFrame to validate
            data_type: Type of data (heroes, builders, user_groups)
            
        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []
        
        # Check if DataFrame is empty
        if df.empty:
            errors.append(f"DataFrame is empty for {data_type}")
            return False, errors
        
        # Check minimum record count
        min_count = self.min_records.get(data_type, 0)
        if len(df) < min_count:
            errors.append(f"Insufficient records for {data_type}: {len(df)} < {min_count}")
        
        # Check required fields
        required_fields = self.required_fields.get(data_type, [])
        missing_fields = [field for field in required_fields if field not in df.columns]
        if missing_fields:
            errors.append(f"Missing required fields for {data_type}: {missing_fields}")
        
        # Check for empty required fields
        for field in required_fields:
            if field in df.columns:
                empty_count = df[field].isna().sum() + (df[field] == '').sum()
                if empty_count > 0:
                    errors.append(f"Empty values in required field '{field}' for {data_type}: {empty_count} records")
        
        # Data type specific validations
        if data_type == "heroes":
            errors.extend(self._validate_heroes(df))
        elif data_type == "builders":
            errors.extend(self._validate_builders(df))
        elif data_type == "user_groups":
            errors.extend(self._validate_user_groups(df))
        
        is_valid = len(errors) == 0
        
        if is_valid:
            self.logger.info(f"Data validation passed for {data_type}: {len(df)} records")
        else:
            self.logger.error(f"Data validation failed for {data_type}: {len(errors)} errors")
            for error in errors:
                self.logger.error(f"  - {error}")
        
        return is_valid, errors
    
    def _validate_heroes(self, df: pd.DataFrame) -> List[str]:
        """Validate AWS Heroes specific data"""
        errors = []
        
        # Check for valid coordinates
        if 'Latitude' in df.columns and 'Longitude' in df.columns:
            invalid_coords = df[
                (df['Latitude'].isna()) | (df['Longitude'].isna()) |
                (df['Latitude'] < -90) | (df['Latitude'] > 90) |
                (df['Longitude'] < -180) | (df['Longitude'] > 180)
            ]
            if len(invalid_coords) > 0:
                errors.append(f"Invalid coordinates in {len(invalid_coords)} hero records")
        
        # Check for valid URLs
        if 'Bio URL' in df.columns:
            invalid_urls = df[
                ~df['Bio URL'].str.startswith('http', na=False)
            ]
            if len(invalid_urls) > 0:
                errors.append(f"Invalid Bio URLs in {len(invalid_urls)} hero records")
        
        # Check for valid categories
        if 'Category' in df.columns:
            valid_categories = [
                'AWS Community Hero', 'AWS Container Hero', 'AWS Data Hero',
                'AWS DevTools Hero', 'AWS Machine Learning Hero', 'AWS Serverless Hero',
                'AWS Storage Hero'
            ]
            invalid_categories = df[
                ~df['Category'].isin(valid_categories)
            ]
            if len(invalid_categories) > 0:
                errors.append(f"Invalid categories in {len(invalid_categories)} hero records")
        
        return errors
    
    def _validate_builders(self, df: pd.DataFrame) -> List[str]:
        """Validate Community Builders specific data"""
        errors = []
        
        # Check for valid coordinates
        if 'Latitude' in df.columns and 'Longitude' in df.columns:
            invalid_coords = df[
                (df['Latitude'].isna()) | (df['Longitude'].isna()) |
                (df['Latitude'] < -90) | (df['Latitude'] > 90) |
                (df['Longitude'] < -180) | (df['Longitude'] > 180)
            ]
            if len(invalid_coords) > 0:
                errors.append(f"Invalid coordinates in {len(invalid_coords)} builder records")
        
        # Check category format (should contain "Builder since")
        if 'Category' in df.columns:
            invalid_categories = df[
                ~df['Category'].str.contains('Builder since', na=False)
            ]
            if len(invalid_categories) > 0:
                errors.append(f"Invalid category format in {len(invalid_categories)} builder records")
        
        return errors
    
    def _validate_user_groups(self, df: pd.DataFrame) -> List[str]:
        """Validate User Groups specific data"""
        errors = []
        
        # Check for valid coordinates
        if 'Latitude' in df.columns and 'Longitude' in df.columns:
            invalid_coords = df[
                (df['Latitude'].isna()) | (df['Longitude'].isna()) |
                (df['Latitude'] < -90) | (df['Latitude'] > 90) |
                (df['Longitude'] < -180) | (df['Longitude'] > 180)
            ]
            if len(invalid_coords) > 0:
                errors.append(f"Invalid coordinates in {len(invalid_coords)} user group records")
        
        # Check for valid URLs
        if 'URL' in df.columns:
            invalid_urls = df[
                ~df['URL'].str.startswith('http', na=False)
            ]
            if len(invalid_urls) > 0:
                errors.append(f"Invalid URLs in {len(invalid_urls)} user group records")
        
        # Check for valid member counts
        if 'Members' in df.columns:
            invalid_members = df[
                (df['Members'].notna()) & 
                ((df['Members'] < 0) | (~df['Members'].astype(str).str.isdigit()))
            ]
            if len(invalid_members) > 0:
                errors.append(f"Invalid member counts in {len(invalid_members)} user group records")
        
        return errors
    
    def clean_dataframe(self, df: pd.DataFrame, data_type: str) -> pd.DataFrame:
        """
        Clean and standardize DataFrame
        
        Args:
            df: DataFrame to clean
            data_type: Type of data (heroes, builders, user_groups)
            
        Returns:
            Cleaned DataFrame
        """
        df_clean = df.copy()
        
        # Remove completely empty rows
        df_clean = df_clean.dropna(how='all')
        
        # Strip whitespace from string columns
        string_columns = df_clean.select_dtypes(include=['object']).columns
        for col in string_columns:
            df_clean[col] = df_clean[col].astype(str).str.strip()
            # Replace 'nan' strings with actual NaN
            df_clean[col] = df_clean[col].replace('nan', pd.NA)
        
        # Clean specific fields based on data type
        if data_type == "heroes":
            df_clean = self._clean_heroes(df_clean)
        elif data_type == "builders":
            df_clean = self._clean_builders(df_clean)
        elif data_type == "user_groups":
            df_clean = self._clean_user_groups(df_clean)
        
        self.logger.info(f"Cleaned {data_type} data: {len(df)} -> {len(df_clean)} records")
        
        return df_clean
    
    def _clean_heroes(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean Heroes specific data"""
        # Standardize category names
        if 'Category' in df.columns:
            category_mapping = {
                'Community Hero': 'AWS Community Hero',
                'Container Hero': 'AWS Container Hero',
                'Data Hero': 'AWS Data Hero',
                'DevTools Hero': 'AWS DevTools Hero',
                'Machine Learning Hero': 'AWS Machine Learning Hero',
                'ML Hero': 'AWS Machine Learning Hero',
                'Serverless Hero': 'AWS Serverless Hero',
                'Storage Hero': 'AWS Storage Hero'
            }
            df['Category'] = df['Category'].replace(category_mapping)
        
        return df
    
    def _clean_builders(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean Builders specific data"""
        # Standardize Bio URL field
        if 'Bio URL' in df.columns:
            df['Bio URL'] = df['Bio URL'].replace(['No URL', 'N/A', ''], pd.NA)
        
        return df
    
    def _clean_user_groups(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean User Groups specific data"""
        # Convert Members to numeric
        if 'Members' in df.columns:
            df['Members'] = pd.to_numeric(df['Members'], errors='coerce')
        
        # Standardize Platform
        if 'Platform' in df.columns:
            df['Platform'] = df['Platform'].str.lower()
        
        return df