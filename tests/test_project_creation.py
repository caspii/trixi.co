from splinter import Browser


def test_game_create():
    """Create a single game. A smoke test"""
    browser = Browser('phantomjs')
    browser.visit('http://localhost:8080')
    browser.find_by_text('Start now').click()
    browser.fill('project_name', 'My awesome test project')
    browser.find_by_text('Next').click()
    for i in range(0, 2):
        browser.fill('people-' + str(i), 'DUDE' + str(i))
    browser.find_by_text('Next').click()
    assert browser.is_text_present('You created a project')
    browser.quit()
