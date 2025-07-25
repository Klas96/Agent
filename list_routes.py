from src.pocketflow.web.app import create_app

app = create_app()

print("PocketFlow Control Panel Routes:")
print("=" * 40)

for rule in app.url_map.iter_rules():
    methods = ','.join(rule.methods - {'HEAD', 'OPTIONS'})
    print(f"{rule.rule:<30} {methods:<15} {rule.endpoint}")

print("\nAccess the control panel at: http://localhost:5001/admin/") 