from splinter import Browser

import tests_lib


def test_previous_projects_list():
    browser = Browser('phantomjs')
    """Test whether previous project cookie is written and gets used correctly"""
    tests_lib.create_project(browser, 'Wicked new test')
    tests_lib.create_project(browser, 'WooHooDoo')
    browser.visit('http://localhost:8080')
    browser.find_by_text('Wicked new test').click()
    assert browser.is_text_present('Wicked new test')
    browser.visit('http://localhost:8080')
    browser.find_by_text('WooHooDoo').click()
    assert browser.is_text_present('WooHooDoo')
    browser.quit()

# def test_clear_previous_games_list():
#     browser = Browser('phantomjs')
#     """Test whether clear previous games works"""
#     tests_lib.create_game(browser, 'Wicked new test game')
#     tests_lib.create_game(browser, 'WooHooDoo')
#     browser.visit('http://localhost:5001')
#     browser.find_link_by_text('Clear this list').click()
#     browser.visit('http://localhost:5001')
#     assert not browser.is_text_present('Wicked new test game')
#     assert not browser.is_text_present('WooHooDoo')
#     browser.quit()
