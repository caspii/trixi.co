from splinter import Browser


def test_task_create():
    """Create a project + tasks."""
    browser = Browser('phantomjs')
    browser.visit('http://localhost:8080')
    browser.find_by_text('Start now').click()
    browser.fill('project_name', 'My awesome test project')
    browser.find_by_id('next').click()
    for i in range(0, 2):
        browser.fill('people-' + str(i), 'DUDE' + str(i))
    browser.find_by_id('next').click()
    assert browser.is_text_present('You created a project')
    browser.find_by_text(' Add task').click()
    browser.fill('title', 'task 1')
    browser.find_by_text('Urgent').click()
    browser.find_by_text(' Save').click()
    assert browser.is_text_present('Urgent')
    assert browser.is_text_present('Assigned to')
