from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import time
from datetime import datetime
from supabase import create_client, Client


url = "https://www.google.com/travel/flights"
urlGuatemala='https://www.google.com/travel/flights?tfs=CBwQARoSagcIARIDWVlacgcIARIDR1VBGhJqBwgBEgNHVUFyBwgBEgNZWVpAAUgBcAGCAQsI____________AZgBAQ&tfu=KgIIAw'
urlIceland='https://www.google.com/travel/flights?tfs=CBwQARoXagcIARIDWVlacgwIAxIIL20vMDZmbGcaF2oMCAMSCC9tLzA2ZmxncgcIARIDWVlaQAFIAXABggELCP___________wGYAQE&tfu=KgIIAw'
urlBarcelona='https://www.google.com/travel/flights?tfs=CBwQARoXagcIARIDWVlacgwIAxIIL20vMDFmNjIaF2oMCAMSCC9tLzAxZjYycgcIARIDWVlaQAFIAXABggELCP___________wGYAQE&tfu=KgIIAw'
urlLisbon='https://www.google.com/travel/flights?tfs=CBwQARoSagcIARIDWVlacgcIARIDTElTGhJqBwgBEgNMSVNyBwgBEgNZWVpAAUgBcAGCAQsI____________AZgBAQ&tfu=KgIIAw'
urlTokyo='https://www.google.com/travel/flights?tfs=CBwQARoXagcIARIDWVlacgwIAxIIL20vMDdkZmsaF2oMCAMSCC9tLzA3ZGZrcgcIARIDWVlaQAFIAXABggELCP___________wGYAQE&tfu=KgIIAw'
urlMexico='https://www.google.com/travel/flights?tfs=CBwQARoYagcIARIDWVlacg0IAxIJL20vMDFxOThtGhhqDQgDEgkvbS8wMXE5OG1yBwgBEgNZWVpAAUgBcAGCAQsI____________AZgBAQ&tfu=KgIIAw'
urlCuba='https://www.google.com/travel/flights?tfs=CBwQARoSagcIARIDWVlacgcIARIDVlJBGhJqBwgBEgNWUkFyBwgBEgNZWVpAAUgBcAGCAQsI____________AZgBAQ&tfu=KgIIAw'
urlWarsaw='https://www.google.com/travel/flights?tfs=CBwQARoXagcIARIDWVlacgwIAxIIL20vMDgxbV8aF2oMCAMSCC9tLzA4MW1fcgcIARIDWVlaQAFIAXABggELCP___________wGYAQE&tfu=KgIIAw'
urlKrakow='https://www.google.com/travel/flights?tfs=CBwQARoXagcIARIDWVlacgwIAxIIL20vMDQ5MXkaF2oMCAMSCC9tLzA0OTF5cgcIARIDWVlaQAFIAXABggELCP___________wGYAQE&tfu=KgIIAw'

locationarr = [urlGuatemala, urlIceland, urlBarcelona, urlLisbon, urlTokyo, urlMexico, urlCuba, urlWarsaw, urlKrakow]
locations = ['guatemala', 'iceland', 'barcelona', 'lisbon', 'tokyo', 'cancun', 'cuba', 'warsaw', 'krakow']
limits = [464, 1, 1, 1, 1, 1, 1, 1, 1]
date_ranges = [
    ("2024-04-05", "2024-04-30"),
    ("2024-03-05", "2024-03-20")
]

driver = webdriver.Chrome()

supabase_url=''
supabase_service_role_key=''

supabase: Client = create_client(supabase_url, supabase_service_role_key)

def find_cheapest_flight(driver, url, locationIndex):
    driver.get(url)
    time.sleep(1)

    departure_date_field = driver.find_element(By.CSS_SELECTOR, 'input[placeholder="Departure"]')
    departure_date_field.click()

    time.sleep(2)

    next_button = driver.find_element(By.CSS_SELECTOR, 'button[jsname="KpyLEe"]') 
    for _ in range(4):
        next_button.click()
        time.sleep(1) 

    time.sleep(2)
    flight_options = driver.find_elements(By.CSS_SELECTOR, 'div[jsname="mG3Az"]')

    # Parse and store flight data
    flight_data = []
    for option in flight_options:
        date = option.get_attribute('data-iso')
        price_element = option.find_element(By.CSS_SELECTOR, 'div[jsname="qCDwBb"]')
        price_text = price_element.text  # Get the text content of the WebElement
        # print(date)
        # print(price_text)
        if(price_text != ''):
            flight_data.append((date, int(price_text.replace('$', '').replace(',', ''))))



    cheapest_flight = None
    for start, finish in date_ranges:
        start_date = datetime.strptime(start, "%Y-%m-%d")
        end_date = datetime.strptime(finish, "%Y-%m-%d")
        print(start)
        print(finish)
        for date_str, price in flight_data:
            flight_date = datetime.strptime(date_str, "%Y-%m-%d")
            if start_date <= flight_date <= end_date:
                if cheapest_flight is None or price < cheapest_flight[1]:
                    cheapest_flight = (date_str, price)

    if cheapest_flight:
        print(f"Cheapest flight for {locations[locationIndex]}: {cheapest_flight[0]} at ${cheapest_flight[1]}")
        location_name = locations[locationIndex]
        price_value = cheapest_flight[1]

        # Insert a new row into the 'price_history' table
        try:
            supabase.table('price_history').insert([
                {'location': location_name, 'price': price_value}
            ]).execute()
        except:
            print('error adding to database')
    else:
        print("No flights found in the specified date range.")
    driver.close()


while True:
    for url in range(len(locationarr)):
        with webdriver.Chrome() as driver:
            find_cheapest_flight(driver, locationarr[url], url)
        time.sleep(5)

    # Wait for 2 hours before next iteration
    time.sleep(7200)  # 7200 seconds = 2 hours