"""Collection of helpful functions that can be used by tests"""


def create_project(browser, game_name):
    """Quick and dirty way of creating a game"""
    browser.visit('http://localhost:8080')
    browser.find_by_text('Start now').click()
    browser.fill('project_name', game_name)
    browser.find_by_id('next').click()
    for i in range(0, 2):
        browser.fill('people-' + str(i), 'DUDE' + str(i))
    browser.find_by_id('next').click()
    assert browser.is_text_present('You created a project')
