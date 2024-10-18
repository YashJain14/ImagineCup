from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException, TimeoutException
from PIL import Image
import io
import time
import os

# Define the classes we want to detect
CLASSES = [
    'link', 'button', 'input', 'select', 'textarea', 'label', 'checkbox', 'radio',
    'dropdown', 'slider', 'toggle', 'menu_item', 'clickable', 'icon'
]

def get_class_id(tag_name, element_type, class_name):
    if 'button' in class_name or tag_name == 'button' or element_type == 'button':
        return CLASSES.index('button')
    elif tag_name == 'a' or element_type == 'link':
        return CLASSES.index('link')
    elif tag_name == 'input':
        if element_type == 'checkbox':
            return CLASSES.index('checkbox')
        elif element_type == 'radio':
            return CLASSES.index('radio')
        else:
            return CLASSES.index('input')
    elif tag_name == 'select' or 'dropdown' in class_name:
        return CLASSES.index('dropdown')
    elif tag_name == 'textarea':
        return CLASSES.index('textarea')
    elif tag_name == 'label':
        return CLASSES.index('label')
    elif 'slider' in class_name or element_type == 'slider':
        return CLASSES.index('slider')
    elif 'toggle' in class_name or element_type == 'switch':
        return CLASSES.index('toggle')
    elif 'menu-item' in class_name or element_type == 'menuitem':
        return CLASSES.index('menu_item')
    elif 'clickable' in class_name:
        return CLASSES.index('clickable')
    elif tag_name == 'i' or tag_name == 'span' and not element_type:
        return CLASSES.index('icon')
    else:
        return -1  # Unknown class

def get_interactive_elements_and_screenshot(url):
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    driver = webdriver.Chrome(options=options)
    
    try:
        driver.get(url)
        WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        
        time.sleep(2)
        
        viewport_metrics = driver.execute_script("""
            return {
                width: window.innerWidth || document.documentElement.clientWidth || document.body.clientWidth,
                height: window.innerHeight || document.documentElement.clientHeight || document.body.clientHeight,
                scrollX: window.pageXOffset,
                scrollY: window.pageYOffset,
                devicePixelRatio: window.devicePixelRatio || 1
            };
        """)
        
        screenshot = driver.get_screenshot_as_png()
        
        interactive_elements = driver.find_elements(By.XPATH, """
            //*[
                self::a or
                self::button or
                self::input or
                self::select or
                self::textarea or
                self::label or
                self::*[@onclick or @role='button' or @role='link' or @role='menuitem' or @role='slider' or
                        @role='scrollbar' or @role='checkbox' or @role='radio' or @role='textbox' or
                        @role='combobox' or @role='listbox' or @role='switch' or @tabindex or
                        contains(@class, 'button') or contains(@class, 'btn') or
                        contains(@class, 'dropdown') or contains(@class, 'menu-item') or
                        contains(@class, 'clickable') or contains(@class, 'selectable')]
            ]
        """)
        
        elements_info = []
        
        for element in interactive_elements:
            try:
                rect = driver.execute_script("""
                    var rect = arguments[0].getBoundingClientRect();
                    return {
                        top: rect.top,
                        left: rect.left,
                        width: rect.width,
                        height: rect.height
                    };
                """, element)
                
                coordinates = {
                    "x1": max(0, rect['left']),
                    "y1": max(0, rect['top']),
                    "x2": min(viewport_metrics['width'], rect['left'] + rect['width']),
                    "y2": min(viewport_metrics['height'], rect['top'] + rect['height'])
                }
                
                if (coordinates['x2'] > 0 and coordinates['y2'] > 0 and
                    coordinates['x1'] < viewport_metrics['width'] and coordinates['y1'] < viewport_metrics['height'] and
                    rect['width'] > 0 and rect['height'] > 0):
                    
                    tag_name = element.tag_name
                    element_type = element.get_attribute("type") or element.get_attribute("role")
                    class_name = element.get_attribute("class") or ""
                    
                    class_id = get_class_id(tag_name, element_type, class_name)
                    
                    if class_id != -1:
                        elements_info.append({
                            "coordinates": coordinates,
                            "class_id": class_id
                        })
            except (StaleElementReferenceException, TimeoutException) as e:
                print(f"Error processing element: {e}")
                continue
        
        return elements_info, screenshot, viewport_metrics
    
    finally:
        driver.quit()

def prepare_yolo_dataset(url, output_dir):
    os.makedirs(output_dir, exist_ok=True)
    
    elements_info, screenshot, viewport_metrics = get_interactive_elements_and_screenshot(url)
    
    image = Image.open(io.BytesIO(screenshot))
    image_width, image_height = image.size
    
    image_filename = f"{output_dir}/image_{int(time.time())}.png"
    image.save(image_filename)
    
    annotation_filename = f"{image_filename[:-4]}.txt"
    
    with open(annotation_filename, 'w') as f:
        for element in elements_info:
            coords = element['coordinates']
            class_id = element['class_id']
            
            x_center = (coords['x1'] + coords['x2']) / (2 * image_width)
            y_center = (coords['y1'] + coords['y2']) / (2 * image_height)
            width = (coords['x2'] - coords['x1']) / image_width
            height = (coords['y2'] - coords['y1']) / image_height
            
            f.write(f"{class_id} {x_center} {y_center} {width} {height}\n")
    
    print(f"Image saved as: {image_filename}")
    print(f"YOLO annotations saved as: {annotation_filename}")

# Save the class list
def save_class_list(output_dir):
    with open(f"{output_dir}/classes.txt", 'w') as f:
        for class_name in CLASSES:
            f.write(f"{class_name}\n")
    print(f"Class list saved as: {output_dir}/classes.txt")

# Example usage
url = "https://www.youtube.com/@YashChopra14"
output_dir = "yolo_dataset"
prepare_yolo_dataset(url, output_dir)
save_class_list(output_dir)

print("Dataset preparation complete.")