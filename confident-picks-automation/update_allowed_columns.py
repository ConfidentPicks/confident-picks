import json

# Update the allowed columns mapping
allowed_columns = {
    'AU': 'predicted_total',
    'AV': 'edge_vs_line', 
    'AW': 'total_confidence',
    'AX': 'predicted_winner',
    'AZ': 'winner_confidence',
    'BA': 'Predicted_Cover_Home',
    'BC': 'home_cover_ confidence',
    'BD': 'Predicted_Cover_Away',
    'BF': 'away_cover_confidence',
    'BG': 'Predicted_Total',
    'BJ': 'total_confidence',
    'BK': 'Predicted_Home_Score',
    'BN': 'Predicted_Away_Score'
}

# Create new mapping with chart columns as READ-ONLY
mapping = {
    'allowed_columns': allowed_columns,
    'readonly_columns': {
        # All original columns A-BP (0-67)
        'A': {'index': 0, 'header': 'game_id'},
        'B': {'index': 1, 'header': 'season'},
        # ... (all original columns remain readonly)
        
        # NEW CHART COLUMNS (BX to CH) - READ ONLY
        'BX': {'index': 75, 'header': 'chart_column_1'},
        'BY': {'index': 76, 'header': 'chart_column_2'},
        'BZ': {'index': 77, 'header': 'chart_column_3'},
        'CA': {'index': 78, 'header': 'chart_column_4'},
        'CB': {'index': 79, 'header': 'chart_column_5'},
        'CC': {'index': 80, 'header': 'chart_column_6'},
        'CD': {'index': 81, 'header': 'chart_column_7'},
        'CE': {'index': 82, 'header': 'chart_column_8'},
        'CF': {'index': 83, 'header': 'chart_column_9'},
        'CG': {'index': 84, 'header': 'chart_column_10'},
        'CH': {'index': 85, 'header': 'chart_column_11'}
    }
}

# Save updated mapping
with open('column_mapping.json', 'w') as f:
    json.dump(mapping, f, indent=2)

print("✅ Updated column mapping:")
print(f"   📝 {len(allowed_columns)} EDITABLE columns")
print(f"   🔒 {len(mapping['readonly_columns'])} READ-ONLY columns")
print(f"   📊 Chart columns BX-CH added to READ-ONLY list")
print(f"   ⚠️  Columns BD & BE are EDITABLE (predictions only)")


