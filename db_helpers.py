"""
Database Helper Functions
=========================
Додаткові утиліти для роботи з Supabase

Usage:
    from db_helpers import export_to_csv, import_from_csv, get_statistics
"""

import pandas as pd
from datetime import datetime
from typing import Optional, Dict, List
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def export_components_to_csv(supabase_client, filename: Optional[str] = None) -> str:
    """
    Експортує всі компоненти з бази даних в CSV файл.
    
    Args:
        supabase_client: Клієнт Supabase
        filename: Назва файлу (опціонально)
    
    Returns:
        str: Шлях до створеного файлу
    """
    try:
        # Fetch all components
        response = supabase_client.table('components').select('*').execute()
        
        if not response.data:
            logger.warning("No components found in database")
            return None
        
        # Convert to DataFrame
        df = pd.DataFrame(response.data)
        
        # Generate filename if not provided
        if not filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f'components_export_{timestamp}.csv'
        
        # Export to CSV
        df.to_csv(filename, index=False, encoding='utf-8-sig')
        logger.info(f"Exported {len(df)} components to {filename}")
        
        return filename
    
    except Exception as e:
        logger.error(f"Export failed: {str(e)}")
        return None


def import_components_from_csv(supabase_client, filename: str) -> Dict:
    """
    Імпортує компоненти з CSV файлу в базу даних.
    
    Args:
        supabase_client: Клієнт Supabase
        filename: Шлях до CSV файлу
    
    Returns:
        Dict: Статистика імпорту
    """
    try:
        # Read CSV
        df = pd.read_csv(filename)
        
        # Validate required columns
        required_cols = ['name', 'type', 'category', 'price_uah', 'stock_status']
        missing_cols = [col for col in required_cols if col not in df.columns]
        
        if missing_cols:
            return {
                'success': False,
                'error': f'Missing columns: {", ".join(missing_cols)}'
            }
        
        # Import each row
        imported = 0
        errors = []
        
        for idx, row in df.iterrows():
            try:
                data = {
                    'name': row['name'],
                    'type': row['type'],
                    'category': row['category'],
                    'price_uah': float(row['price_uah']),
                    'stock_status': bool(row['stock_status']),
                    'url': row.get('url', '')
                }
                
                supabase_client.table('components').insert(data).execute()
                imported += 1
                
            except Exception as e:
                errors.append(f"Row {idx}: {str(e)}")
        
        return {
            'success': True,
            'imported': imported,
            'total': len(df),
            'errors': errors
        }
    
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }


def get_database_statistics(supabase_client) -> Dict:
    """
    Отримує статистику бази даних.
    
    Args:
        supabase_client: Клієнт Supabase
    
    Returns:
        Dict: Статистика
    """
    try:
        # Fetch all components
        response = supabase_client.table('components').select('*').execute()
        
        if not response.data:
            return {
                'total_components': 0,
                'in_stock': 0,
                'out_of_stock': 0,
                'by_type': {},
                'by_category': {},
                'price_range': {},
                'avg_price': 0
            }
        
        df = pd.DataFrame(response.data)
        
        # Calculate statistics
        stats = {
            'total_components': len(df),
            'in_stock': len(df[df['stock_status'] == True]),
            'out_of_stock': len(df[df['stock_status'] == False]),
            'by_type': df['type'].value_counts().to_dict(),
            'by_category': df['category'].value_counts().to_dict(),
            'price_range': {
                'min': float(df['price_uah'].min()),
                'max': float(df['price_uah'].max()),
                'median': float(df['price_uah'].median())
            },
            'avg_price': float(df['price_uah'].mean())
        }
        
        return stats
    
    except Exception as e:
        logger.error(f"Failed to get statistics: {str(e)}")
        return {}


def search_components(supabase_client, query: str, 
                     search_in: List[str] = ['name', 'category']) -> pd.DataFrame:
    """
    Пошук компонентів по ключовому слову.
    
    Args:
        supabase_client: Клієнт Supabase
        query: Пошуковий запит
        search_in: Поля для пошуку
    
    Returns:
        pd.DataFrame: Знайдені компоненти
    """
    try:
        # Fetch all components
        response = supabase_client.table('components').select('*').execute()
        
        if not response.data:
            return pd.DataFrame()
        
        df = pd.DataFrame(response.data)
        
        # Search in specified fields
        mask = pd.Series([False] * len(df))
        
        for field in search_in:
            if field in df.columns:
                mask |= df[field].str.contains(query, case=False, na=False)
        
        return df[mask]
    
    except Exception as e:
        logger.error(f"Search failed: {str(e)}")
        return pd.DataFrame()


def duplicate_component(supabase_client, component_id: int, 
                       new_name: Optional[str] = None) -> bool:
    """
    Дублює компонент в базі даних.
    
    Args:
        supabase_client: Клієнт Supabase
        component_id: ID компонента для дублювання
        new_name: Нова назва (опціонально)
    
    Returns:
        bool: Успішність операції
    """
    try:
        # Fetch original component
        response = supabase_client.table('components').select('*').eq('id', component_id).execute()
        
        if not response.data:
            logger.error(f"Component {component_id} not found")
            return False
        
        original = response.data[0]
        
        # Create duplicate
        duplicate = {
            'name': new_name or f"{original['name']} (копія)",
            'type': original['type'],
            'category': original['category'],
            'price_uah': original['price_uah'],
            'stock_status': original['stock_status'],
            'url': original['url']
        }
        
        supabase_client.table('components').insert(duplicate).execute()
        logger.info(f"Component {component_id} duplicated successfully")
        
        return True
    
    except Exception as e:
        logger.error(f"Duplication failed: {str(e)}")
        return False


def bulk_update_stock_status(supabase_client, component_ids: List[int], 
                             status: bool) -> Dict:
    """
    Масове оновлення статусу наявності.
    
    Args:
        supabase_client: Клієнт Supabase
        component_ids: Список ID компонентів
        status: Новий статус
    
    Returns:
        Dict: Результат операції
    """
    try:
        updated = 0
        errors = []
        
        for comp_id in component_ids:
            try:
                supabase_client.table('components').update(
                    {'stock_status': status}
                ).eq('id', comp_id).execute()
                updated += 1
            except Exception as e:
                errors.append(f"ID {comp_id}: {str(e)}")
        
        return {
            'success': True,
            'updated': updated,
            'total': len(component_ids),
            'errors': errors
        }
    
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }


def get_price_history(supabase_client, component_id: int) -> pd.DataFrame:
    """
    Отримує історію змін цін (для майбутньої реалізації).
    
    Args:
        supabase_client: Клієнт Supabase
        component_id: ID компонента
    
    Returns:
        pd.DataFrame: Історія цін
    """
    # TODO: Implement when price_history table is created
    logger.warning("Price history feature not implemented yet")
    return pd.DataFrame()


if __name__ == "__main__":
    # Test functions
    print("Database helpers module loaded successfully")
    print("Available functions:")
    print("  - export_components_to_csv")
    print("  - import_components_from_csv")
    print("  - get_database_statistics")
    print("  - search_components")
    print("  - duplicate_component")
    print("  - bulk_update_stock_status")
    print("  - get_price_history")
