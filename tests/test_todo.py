import pytest
from homeassistant.components.google_tasks.todo import GoogleTaskTodoListEntity
from datetime import date, timedelta


@pytest.fixture
def google_task_entity():
    """Fixture to create an instance of the GoogleTaskTodoListEntity class."""
    # Mocking the coordinator and initialization data
    mock_coordinator = None  # Replace with a mock if you need one
    google_task_entity = GoogleTaskTodoListEntity(
        coordinator=mock_coordinator,
        name="Test List",
        config_entry_id="test_config_id",
        task_list_id="test_task_list_id",
    )
    return google_task_entity


def test_categorize_tasks_today(google_task_entity):
    """Test that tasks due today are categorized as 'Today'."""
    current_date = date.today()
    mock_tasks = [
        {"title": "Task 1", "due": current_date.isoformat()},
        {"title": "Task 2", "due": current_date.isoformat()},
    ]

    categorized_tasks = google_task_entity.categorize_tasks(mock_tasks)

    assert len(categorized_tasks["Today"]) == 2
    assert categorized_tasks["Today"][0]["title"] == "Task 1"
    assert categorized_tasks["Today"][1]["title"] == "Task 2"


def test_categorize_tasks_this_week(google_task_entity):
    """Test that tasks due this week (excluding today) are categorized as 'This Week'."""
    current_date = date.today()
    week_end = current_date + timedelta(
        days=6 - current_date.weekday()
    )  # End of the week

    # Modify the due dates to ensure they are within this week (including week_end)
    mock_tasks = [
        {
            "title": "Task 3",
            "due": (current_date + timedelta(days=1)).isoformat(),
        },  # Tomorrow
        {"title": "Task 4", "due": week_end.isoformat()},  # End of this week
    ]

    categorized_tasks = google_task_entity.categorize_tasks(mock_tasks)

    # Both tasks should be in "This Week"
    assert len(categorized_tasks["This Week"]) == 2
    assert categorized_tasks["This Week"][0]["title"] == "Task 3"
    assert categorized_tasks["This Week"][1]["title"] == "Task 4"


def test_categorize_tasks_upcoming(google_task_entity):
    """Test that tasks due after this week are categorized as 'Upcoming'."""
    current_date = date.today()
    week_end = current_date + timedelta(days=6 - current_date.weekday())

    mock_tasks = [
        {"title": "Task 5", "due": (week_end + timedelta(days=1)).isoformat()},
        {"title": "Task 6", "due": (week_end + timedelta(days=3)).isoformat()},
    ]

    categorized_tasks = google_task_entity.categorize_tasks(mock_tasks)

    assert len(categorized_tasks["Upcoming"]) == 2
    assert categorized_tasks["Upcoming"][0]["title"] == "Task 5"
    assert categorized_tasks["Upcoming"][1]["title"] == "Task 6"


def test_categorize_tasks_mixed(google_task_entity):
    """Test that tasks due today, this week, and upcoming are categorized correctly."""
    current_date = date.today()
    week_end = current_date + timedelta(days=6 - current_date.weekday())

    mock_tasks = [
        {"title": "Task 1", "due": current_date.isoformat()},  # Today
        {
            "title": "Task 2",
            "due": (current_date + timedelta(days=2)).isoformat(),
        },  # Upcoming (not This Week)
        {
            "title": "Task 3",
            "due": (week_end + timedelta(days=1)).isoformat(),
        },  # Upcoming (after week_end)
    ]

    categorized_tasks = google_task_entity.categorize_tasks(mock_tasks)

    assert len(categorized_tasks["Today"]) == 1
    assert categorized_tasks["Today"][0]["title"] == "Task 1"

    # Updated to reflect that Task 2 is now in "Upcoming"
    assert len(categorized_tasks["This Week"]) == 0

    assert len(categorized_tasks["Upcoming"]) == 2
    assert categorized_tasks["Upcoming"][0]["title"] == "Task 2"
    assert categorized_tasks["Upcoming"][1]["title"] == "Task 3"
