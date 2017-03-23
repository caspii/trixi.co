from splinter import Browser


def test_game_name_empty():
    """Test form validation on first page"""
    browser = Browser('phantomjs')
    browser.visit('http://localhost:8080/new')
    browser.find_by_id('next').click()
    assert browser.is_text_present('This field is required.')
    browser.quit()


def test_person_button():
    """Test that person number does not go below 2 via button press"""
    browser = Browser('phantomjs')
    browser.visit('http://localhost:8080/new')
    browser.fill('project_name', 'Testing one two three')
    browser.find_by_text('-').click()
    browser.find_by_text('-').click()
    browser.find_by_text('-').click()
    browser.find_by_id('next').click()
    assert browser.is_text_present("Who's involved?")
    browser.quit()


def test_too_few_people():
    """Test that person number does not go below 2 via button press"""
    browser = Browser('phantomjs')
    browser.visit('http://localhost:8080/new')
    browser.fill('project_name', 'Testing one two three')
    browser.fill('person_count', '-10')
    browser.find_by_id('next').click()
    assert browser.is_text_present('Number must be between')
    browser.quit()
