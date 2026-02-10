# Integrating Consumer Price Index into KIP

## How to Use Sectoral Price Trends

### 1. User Inputs Business Sector Interest

```python
user_interest = 'Food business'
user_capital = 10000
user_location = 'Lusaka'
```

### 2. Check Sector Price Trend

```python
# Map user interest to CPI sector
sector_map = {
    'food': 'Food and non-alcoholic beverages',
    'transport': 'Transport',
    'education': 'Education',
    # ... etc
}

sector = sector_map.get(user_interest.lower())
trend = cpi_analyzer.sector_trends[
    cpi_analyzer.sector_trends['sector'] == sector
]
yoy_change = trend['yoy_change_pct'].values[0]
```

### 3. Adjust Recommendation Based on Trend

```python
if yoy_change > overall_inflation + 3:
    advice = f"""
    ✅ STRONG OPPORTUNITY
    This sector is growing {yoy_change:.1f}% (above average).
    Consumers willing to pay premium prices.
    Recommend: Supply-side businesses, premium offerings
    """

elif yoy_change > overall_inflation:
    advice = f"""
    ⚠️  MODERATE OPPORTUNITY
    Growing at {yoy_change:.1f}%, slightly above average.
    Recommend: Efficiency focus, good quality at fair price
    """

else:
    advice = f"""
    ❌ CHALLENGING SECTOR
    Growing at {yoy_change:.1f}%, below average.
    High competition, tight margins.
    Recommend: Only if you have unique advantage
    """
```

### 4. Combine with Other Factors

```python
# Final KIP recommendation combines:
# - CPI sector trend (price dynamics)
# - Market saturation (competition)
# - User capital (feasibility)
# - Location demographics (demand)
# - Economic forecast (GDP, inflation)
```
