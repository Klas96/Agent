from control_panel import app

with app.app_context():
    for rule in app.url_map.iter_rules():
        print(f"{rule.endpoint:30s} {rule.methods} {rule.rule}") 