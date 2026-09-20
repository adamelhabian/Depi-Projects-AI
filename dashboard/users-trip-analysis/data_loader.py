from dashboard.database import load_dashboard_data


def load_clean_data():
    df = load_dashboard_data()
    return df