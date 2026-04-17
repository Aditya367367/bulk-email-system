import pandas as pd

# Sample data for testing
data = [
    {
        'name': 'John Smith',
        'email': 'john.smith@example.com',
        'license_number': 'LC-2024-001',
        'validity_from': '2024-01-15',
        'premises_type': 'Retail',
        'category': 'Food Service',
        'address': '123 Main St, New York, NY 10001'
    },
    {
        'name': 'Jane Johnson',
        'email': 'jane.johnson@example.com',
        'license_number': 'LC-2024-002',
        'validity_from': '2024-02-20',
        'premises_type': 'Restaurant',
        'category': 'Food Service',
        'address': '456 Oak Ave, Los Angeles, CA 90001'
    },
    {
        'name': 'Mike Wilson',
        'email': 'mike.wilson@example.com',
        'license_number': 'LC-2024-003',
        'validity_from': '2024-03-10',
        'premises_type': 'Retail',
        'category': 'General',
        'address': '789 Pine Rd, Chicago, IL 60007'
    },
    {
        'name': 'Sarah Davis',
        'email': 'sarah.davis@example.com',
        'license_number': 'LC-2024-004',
        'validity_from': '2024-01-25',
        'premises_type': 'Restaurant',
        'category': 'Food Service',
        'address': '321 Elm St, Houston, TX 77001'
    },
    {
        'name': 'Tom Brown',
        'email': 'tom.brown@example.com',
        'license_number': 'LC-2024-005',
        'validity_from': '2024-04-05',
        'premises_type': 'Retail',
        'category': 'General',
        'address': '654 Maple Dr, Phoenix, AZ 85001'
    }
]

# Create DataFrame
df = pd.DataFrame(data)

# Save to Excel file
df.to_excel('/home/aditya367/Desktop/email bulk system/test_data/sample_emails_5.xlsx', index=False)

print("Created sample_emails_5.xlsx with 5 test records")

# Create a larger file with 20 records
large_data = []
for i in range(1, 21):
    large_data.append({
        'name': f'Test User {i}',
        'email': f'testuser{i}@example.com',
        'license_number': f'LC-2024-{i:03d}',
        'validity_from': f'2024-{(i % 12) + 1:02d}-{(i % 28) + 1:02d}',
        'premises_type': ['Retail', 'Restaurant', 'Office'][i % 3],
        'category': ['Food Service', 'General', 'Medical'][i % 3],
        'address': f'{i * 100} Test Street, City {i}, State {i:05d}'
    })

df_large = pd.DataFrame(large_data)
df_large.to_excel('/home/aditya367/Desktop/email bulk system/test_data/sample_emails_20.xlsx', index=False)
print("Created sample_emails_20.xlsx with 20 test records")

# Create a file with exactly 100 records (maximum allowed)
max_data = []
for i in range(1, 101):
    max_data.append({
        'name': f'Max Test User {i}',
        'email': f'maxtest{i}@example.com',
        'license_number': f'LC-2024-{i:03d}',
        'validity_from': f'2024-{(i % 12) + 1:02d}-{(i % 28) + 1:02d}',
        'premises_type': ['Retail', 'Restaurant', 'Office', 'Warehouse'][i % 4],
        'category': ['Food Service', 'General', 'Medical', 'Industrial'][i % 4],
        'address': f'{i * 10} Max Avenue, Metro {i}, Province {i:05d}'
    })

df_max = pd.DataFrame(max_data)
df_max.to_excel('/home/aditya367/Desktop/email bulk system/test_data/sample_emails_100.xlsx', index=False)
print("Created sample_emails_100.xlsx with 100 test records (maximum allowed)")
