
import pandas as pd
from app import answer_question


# Sample sales data for testing
def sample_data():
    return pd.DataFrame({
        "Product": ["Laptop", "Phone", "Laptop", "Phone"],
        "Region": ["North", "South", "South", "North"],
        "Month": ["2026-01", "2026-01", "2026-02", "2026-02"],
        "Revenue": [1000, 500, 1500, 700]
    })


def test_total_revenue():
    answer, result = answer_question(
        "What is the total revenue?", sample_data()
    )
    assert "3,700.00" in answer


def test_highest_revenue_product():
    answer, result = answer_question(
        "Which product generated the highest revenue?",
        sample_data()
    )
    assert "Laptop" in answer


def test_monthly_revenue_trend():
    answer, result = answer_question(
        "Show monthly revenue trend", sample_data()
    )
    assert len(result) == 2


def test_highest_revenue_region():
    answer, result = answer_question(
        "Which region generated the highest sales?",
        sample_data()
    )
    assert "South" in answer


def test_month_to_month_change():
    answer, result = answer_question(
        "How did revenue change between 2026-01 and 2026-02?",
        sample_data()
    )
    assert "700.00" in answer
    assert "46.67%" in answer


def test_empty_question():
    answer, result = answer_question("", sample_data())
    assert "Please enter a question" in answer


def test_unsupported_question():
    answer, result = answer_question(
        "What is the weather today?", sample_data()
    )
    assert "couldn't identify" in answer
