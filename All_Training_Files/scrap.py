from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import json, csv, time

def scrape(num_stories):
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    driver.set_page_load_timeout(30)
    
    stories = []
    page = 1
    
    while len(stories) < num_stories:
        url = f"https://www.urdupoint.com/kids/category/moral-stories{'-page'+str(page) if page>1 else ''}.html"
        try:
            driver.get(url)
            time.sleep(3)
        except:
            print(f"Page {page} timeout, skipping...")
            page += 1
            continue
        
        links = [a.get_attribute('href') for a in driver.find_elements(By.CSS_SELECTOR, 'a.sharp_box')]
        if not links:
            break
        
        print(f"Page {page}: {len(links)} stories")
        
        for link in links:
            if len(stories) >= num_stories:
                break
            
            try:
                driver.get(link)
                time.sleep(3)
                
                title = driver.find_element(By.CSS_SELECTOR, 'h1.phead').text
                content = driver.find_element(By.CSS_SELECTOR, 'div.txt_detail').text.strip()
                
                if len(content) > 100:
                    stories.append({'num': len(stories)+1, 'title': title, 'content': content, 'url': link})
                    print(f"Story {len(stories)}: {title[:40]}")
            except:
                print(f"Failed")
        
        page += 1
    
    driver.quit()
    return stories

stories = scrape(500)

if stories:
    with open('stories.json', 'w', encoding='utf-8') as f:
        json.dump(stories, f, ensure_ascii=False, indent=2)
    
    with open('stories.csv', 'w', encoding='utf-8-sig', newline='') as f:
        w = csv.DictWriter(f, fieldnames=['num','title','content','url'])
        w.writeheader()
        w.writerows(stories)
    
    print(f"\nSaved {len(stories)} stories!")
else:
    print("No stories")